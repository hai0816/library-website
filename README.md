### Dự án Quản lý Thư viện (Library Website)

Một trang web hỗ trợ quản lý sách, độc giả và quá trình mượn trả sách trong thư viện một cách hiệu quả và trực quan. 

### 🚀 Tính năng chính

* **Quản lý sách:** Thêm, sửa, xóa và phân loại các đầu sách trong thư viện.
* **Quản lý người dùng:** Phân quyền giữa thủ thư (Admin) và người đọc (User).
* **Mượn/Trả sách:** Ghi nhận lịch sử mượn trả, tính ngày quá hạn.
* **Tìm kiếm thông minh:** Tìm sách nhanh theo tên, tác giả hoặc thể loại.

### 🛠️ Công nghệ sử dụng

* **Backend:** Python (Flask / Django)
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
* **Database:** SQLite / MySQL

### 💻 Hướng dẫn cài đặt và chạy dự án

### Điều kiện tiên quyết

Máy tính của bạn cần cài đặt sẵn **Python** (phiên bản 3.8 trở lên) và **Git**. 

### Các bước thực hiện

1. **Cloning dự án về máy cục bộ:** 

bash

git clone https://github.com/hai0816/library-website.git
cd library-website

Hãy thận trọng khi sử dụng mã.
2. **Tạo và kích hoạt môi trường ảo (Khuyên dùng):** 

  * **Windows:** 

bash

python -m venv venv
.\venv\Scripts\activate

Hãy thận trọng khi sử dụng mã.
  * **macOS/Linux:** 

bash

python3 -m venv venv
source venv/bin/activate

Hãy thận trọng khi sử dụng mã.
3. **Cài đặt các thư viện bắt buộc:** 

bash

pip install -r requirements.txt

Hãy thận trọng khi sử dụng mã.
4. **Khởi chạy ứng dụng:** 

bash

python run.py

Hãy thận trọng khi sử dụng mã.

Mở trình duyệt và truy cập đường dẫn: http://127.0.0.1:5000 (hoặc cổng hiển thị trên terminal) để xem website.
