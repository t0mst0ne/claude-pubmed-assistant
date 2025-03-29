from typing import Callable, Dict, List, Tuple, Any, Optional, Union

def asgi_to_wsgi_app(wsgi_app: Callable) -> Callable:
    """
    將WSGI應用轉換為ASGI應用
    """
    async def asgi_app(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        """
        ASGI應用
        """
        if scope["type"] != "http":
            return
        
        # 從ASGI參數構建WSGI環境
        environ = {
            "REQUEST_METHOD": scope["method"],
            "SCRIPT_NAME": "",
            "PATH_INFO": scope["path"],
            "QUERY_STRING": scope["query_string"].decode("ascii"),
            "SERVER_PROTOCOL": "HTTP/" + scope["http_version"],
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": scope.get("scheme", "http"),
            "wsgi.input": WSGIHTTPInputWrapper(receive),
            "wsgi.errors": scope.get("stderr", None),
            "wsgi.multithread": True,
            "wsgi.multiprocess": True,
            "wsgi.run_once": False,
        }
        
        # 添加HTTP頭部
        for name, value in scope.get("headers", []):
            name = name.decode("ascii")
            value = value.decode("ascii")
            if name == "content-length":
                environ["CONTENT_LENGTH"] = value
            elif name == "content-type":
                environ["CONTENT_TYPE"] = value
            else:
                environ["HTTP_" + name.upper().replace("-", "_")] = value
                
        # 添加服務器和客戶端地址信息
        if "server" in scope:
            environ["SERVER_NAME"] = scope["server"][0]
            environ["SERVER_PORT"] = str(scope["server"][1])
        if "client" in scope:
            environ["REMOTE_ADDR"] = scope["client"][0]
            environ["REMOTE_PORT"] = str(scope["client"][1])
            
        # 創建回調函數來發送響應
        sent = []
        
        async def send_start(status, headers):
            status_code = int(status.split()[0])
            sent.append(True)
            await send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    [name.lower().encode("ascii"), value.encode("ascii")]
                    for name, value in headers
                ],
            })
            
        async def send_body(body):
            if not sent:
                await send_start("200 OK", [])
            await send({
                "type": "http.response.body",
                "body": body,
                "more_body": False,
            })
            
        # 執行WSGI應用
        result = await run_wsgi_app(wsgi_app, environ, send_start, send_body)
        
        # 如果應用返回響應體，發送它
        if result and not sent:
            await send_body(result)
    
    return asgi_app


class WSGIHTTPInputWrapper:
    """
    包裝從ASGI接收器獲取的HTTP請求體
    """
    def __init__(self, receive: Callable) -> None:
        self.receive = receive
        self.buffer = b""
        self.eof = False
        
    async def read(self, size: Optional[int] = None) -> bytes:
        """
        從請求體讀取指定大小的數據
        """
        if size is None:
            # 讀取全部
            while not self.eof:
                await self._receive_more()
            data = self.buffer
            self.buffer = b""
            return data
            
        if size <= 0:
            return b""
            
        while len(self.buffer) < size and not self.eof:
            await self._receive_more()
            
        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return data
        
    async def _receive_more(self) -> None:
        """
        從ASGI接收器獲取更多數據
        """
        if self.eof:
            return
            
        message = await self.receive()
        if message["type"] != "http.request":
            return
            
        self.buffer += message.get("body", b"")
        if not message.get("more_body", False):
            self.eof = True


async def run_wsgi_app(wsgi_app: Callable, environ: Dict[str, Any], 
                      send_start: Callable, send_body: Callable) -> bytes:
    """
    執行WSGI應用並獲取響應
    """
    # WSGI響應回調
    response_status = ["200 OK"]
    response_headers = []
    response_body = []
    
    def start_response(status: str, headers: List[Tuple[str, str]], 
                       exc_info: Optional[Any] = None) -> Callable:
        response_status[0] = status
        response_headers[:] = headers
        return lambda body: response_body.append(body)
    
    # 執行WSGI應用
    loop = asyncio.get_event_loop()
    wsgi_response = await loop.run_in_executor(
        None, 
        lambda: b"".join(wsgi_app(environ, start_response) or [])
    )
    
    # 發送響應頭
    await send_start(response_status[0], response_headers)
    
    # 返回響應體
    return wsgi_response + b"".join(response_body)
