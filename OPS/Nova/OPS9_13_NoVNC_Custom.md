# NoVNC - Customization

# 1. RFB

- Remote Farme Buffer là một giao thức cung cấp việc điều khiển từ xa thông qua giao diện đồ họa
- Hỗ trợ tất cả các hệ điều hành và được sử dụng trong VNC
- noVNC sử dụng RFB + JS để tương tác với máy ảo (Guest)

# 2. Thiết lập Lab

...

# 3. Các tính năng sẵn có & triển khai thêm

## 3.1. Base

- Sử dụng file vnc_lite.html của noVNC

[https://github.com/novnc/noVNC/blob/master/vnc_lite.html](https://github.com/novnc/noVNC/blob/master/vnc_lite.html)

- Chỉ có sẵn chức năng Send Ctrl + Alt + Del

```bash
<div id="sendCtrlAltDelButton">Send CtrlAltDel</div> // Frontend cua Button

//CSS cua button
#sendCtrlAltDelButton {
            position: fixed;
            top: 0px;
            right: 0px;
            border: 1px outset;
            padding: 5px 5px 4px 5px;
            cursor: pointer;
}

//Xu ly khi click Button (Thuc thi Function sendCtrlAltDel)

document.getElementById('sendCtrlAltDelButton').onclick = sendCtrlAltDel;

//Function sendCtrlAltDel
function sendCtrlAltDel() {
            rfb.sendCtrlAltDel(); //Goi Methods sendCtrlAltDel cua rfb
            return false;
}

```

## 3.2. Send Text

- Tính năng cho phép người dùng gửi Text vào máy ảo
- Flow hoạt động

- Code

```bash
function sendText(){
/Hien thi Prompt de User nhap text
            var inputText = prompt("Please Enter the text to send to Console: ");
            if(inputText != null){ //Kiem tra chuoi co rong hay khong
                for(let i = 0; i < inputText.length; i++){
                //Gui tung ki tu vao may ao qua method rfb.sendKey()
                    rfb.sendKey(inputText.charCodeAt(i), true);
                }
            }else{
            //Thong bao chuoi bi rong
                alert("The input is empty");
            }
        }
```

## 3.2. Capture Screen

- Giúp User có thể chụp ảnh màn hình máy ảo
- User click Capture Screen, chương trình tự động chụp màn hình máy ảo, tạo file .png và tải về máy User
- Code

```bash
function captureScreen(){
// Dung method toDataURL("png") cua rfb de chup lai man hinh
            var pngData = rfb.toDataURL("png");
// Tao link Download
            var downloadLink = document.createElement('a');
            downloadLink.href = pngData;
            downloadLink.download = "image.png"; //Dat ten file la image.png
            downloadLink.click(); //Tai file ve may User
        }
```

## 3.3. Disconnect

- Sử dụng đê ngắt kết nối VNC với máy ảo
- Code

```bash
function disconnectButton(){
            rfb.disconnect(); // Dung method disconnect cua rfb
        }
```

## 3.4. Virtual Keyboard

- Cung cấp bàn phím ảo để người dùng điện thoại, touch device có thể nhập liệu vào máy ảo một cách dễ dàng
- Sử dụng simple-keyboard viết bằng JS https://github.com/hodgef/simple-keyboard
- Code

```bash
//Load code cua Keyboard

<script src="https://cdn.jsdelivr.net/npm/simple-keyboard@latest/build/index.js"></script>

//Load CSS cua Keyboard

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/simple-keyboard@latest/build/css/index.css">

//Hien thi Keyboard

<div class="simple-keyboard"></div>

//Show/Hide Keyboard Button

<button id="toggleButton" class="button">Show/Hide Keyboard</button>

//Chuc nang an hien ban phim
const toggleButton = document.getElementById("toggleButton");
        const keyboardDiv = document.querySelector(".simple-keyboard");
    
        toggleButton.addEventListener("click", () => {
            keyboardDiv.classList.toggle("hidden");
        }); 

//Khoi tao Keyboard
const Keyboard = window.SimpleKeyboard.default;
        const myKeyboard = new Keyboard({
            onChange: input => onChange(input),
            onKeyPress: button => onKeyPress(button)
        });
 //Xu ly khi nhan phim - Gui phim vao may ao qua rfb
 function onKeyPress(button) {
            if(button === '{bksp}'){
                rfb.sendKey(0xFF08);
            }
            else if(button === '{tab}'){
                rfb.sendKey(0xFF09);
            }else if(button === '{enter}'){
                rfb.sendKey(0xFF0D);
            }else if(button === '{space}'){
                rfb.sendKey(0x0020);
            }else if(button === '.com'){
                var inputText = '.com';
                for(let i = 0; i < inputText.length; i++){
                    rfb.sendKey(inputText.charCodeAt(i), true);
                }
            }else if(button === '{shift}'){
                
            }else if(button === '{lock}'){
                rfb.sendKey(0xffe5);
            }else{
                rfb.sendKey(button.charCodeAt(0), true);
            }
            
        }
```

# 4. Cài đặt

- File đã Customized xong là file vnc_customized.html
- Copy để vào thư mục Source Code noVNC
- Chạy noVNC

```bash
~/noVNC/utils/novnc_proxy --vnc localhost:5901
```

- Truy cập đường dẫn: http://IPHOST::6080/vnc_customized.html?host=HOST&port=6080