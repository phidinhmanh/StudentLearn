# Tài liệu Thiết kế Giao diện (UI/UX Design Spec)

Tài liệu hướng dẫn triển khai giao diện người dùng (UI) và trải nghiệm người dùng (UX) trên nền tảng Android (Jetpack Compose).

## 1. Ứng dụng 8 Quy tắc Vàng của Shneiderman

Thiết kế của StudentLearn tuân thủ nghiêm ngặt các nguyên tắc sau:
1. **Strive for consistency (Nhất quán):** Các button Call-to-action chính luôn ở dưới cùng màn hình (bottom-anchored). Font chữ và màu sắc tuân thủ Design System.
2. **Enable frequent users to use shortcuts (Phím tắt):** Có thanh tìm kiếm (Search bar) và các chip lọc (Filters: "Cần học lại", "Chưa học", "Đã master") ở màn hình Home để truy cập nhanh.
3. **Offer informative feedback (Phản hồi thông tin):** 
   - Khi chọn đáp án Quiz: Màu xanh lá báo đúng, đỏ rung nhẹ báo sai.
   - Khi Submit form: Hiển thị trạng thái Loading (CircularProgressIndicator).
4. **Design dialog to yield closure (Đóng gói tương tác):** Màn hình "Hoàn thành bài tập" là điểm kết thúc rõ ràng, hiển thị biểu tượng pháo hoa và mascot Cheems chúc mừng.
5. **Offer simple error handling (Xử lý lỗi đơn giản):** Khi mất mạng hoặc API lỗi, hiển thị Snackbar với nút "Thử lại" (Retry action) thay vì crash app.
6. **Permit easy reversal of actions (Cho phép hoàn tác):** Có nút "Quay lại" rõ ràng trên TopAppBar, hoặc vuốt từ cạnh viền (Gesture Navigation) để hủy hành động.
7. **Support internal locus of control (Quyền kiểm soát):** Người dùng chủ động xem sơ đồ (Pinch-to-zoom, Pan) và quyết định học node nào, không bị ép buộc tuyến tính.
8. **Reduce short-term memory load (Giảm tải bộ nhớ ngắn hạn):** Khi trả lời quiz, các dữ kiện, hint, và công thức được hiển thị cố định trong một Card, người dùng không cần phải ghi nhớ hay lật lại trang trước.

## 2. Design System (Hệ thống Thiết kế)

### 2.1. Bảng màu (Ember Theme)
Chúng ta sử dụng triết lý Dark Mode làm chủ đạo để giảm mỏi mắt cho học sinh khi học buổi tối, kết hợp điểm nhấn màu Hổ phách (Amber) tượng trưng cho "Ngọn lửa tri thức".
- **Primary:** Màu Cam Amber (`#FFB300`) - Dùng cho nút bấm chính, ngọn lửa streak.
- **Secondary:** Cam nhạt (`#FFE5B4`) - Dùng cho Text highlight, thẻ phụ.
- **Background:** Đen sâu (`#121212`) - Nền tổng thể của ứng dụng.
- **Surface:** Xám đậm (`#1E1E1E`) - Nền của các Card, Dialog, Bottom Sheet.
- **Success:** Xanh lá (`#00C853`) - Trả lời đúng, Level Master.
- **Error:** Đỏ (`#CF6679`) - Trả lời sai, Cần học lại.

### 2.2. Typography (Kiểu chữ)
- **Headings & Body:** `Inter` - Font chữ hiện đại, rõ ràng, dễ đọc trên màn hình điện thoại.
  - H1: 24sp, Bold
  - Body1: 16sp, Regular
- **Công thức & Code:** `JetBrains Mono` - Font monospaced dùng để hiển thị công thức Toán (LaTeX) hoặc mã nguồn để đảm bảo canh lề chuẩn xác.

### 2.3. Corner Radius (Độ bo góc)
- **Button:** `RoundedCornerShape(24.dp)` - Bo tròn mạnh tạo sự thân thiện (Pill shape).
- **Card/Container:** `RoundedCornerShape(16.dp)` - Bo góc vừa phải tạo khối vững chắc.

## 3. Wireframes / Mockups (5 Màn hình chính)

1. **Màn hình Onboarding:**
   - **Top:** Ảnh minh họa Mascot Cheems đang thắp sáng ngọn lửa.
   - **Center:** Tiêu đề "Khám phá Lỗ hổng Tri thức của bạn".
   - **Bottom:** Nút "Bắt đầu ngay" lớn, màu Primary.
2. **Màn hình Home (Dashboard):**
   - **Header:** Lời chào + Trạng thái Streak (Biểu tượng ngọn lửa + số ngày). Mascot Cheems hiển thị dựa theo performance hôm qua.
   - **Body:** Card "Tiếp tục học" gợi ý node cần học tiếp. Bên dưới là danh sách các Topic đang học dở dang.
   - **Bottom:** BottomNavigationBar (Home, Graph, Profile).
3. **Màn hình Graph (Bản đồ tri thức):**
   - Giao diện chiếm toàn màn hình (Full-screen canvas).
   - Các Node liên kết bằng đoạn thẳng. Người dùng dùng hai ngón tay để Zoom In/Out.
   - Click vào một Node -> Bottom Sheet trượt lên hiển thị thông tin Node và nút "Làm bài Quiz".
4. **Màn hình Quiz:**
   - **TopAppBar:** Có thanh Progress Bar (ví dụ: Câu 2/5).
   - **Body:** Card chứa Nội dung câu hỏi (Render LaTeX). Bên dưới là 4 Card nhỏ chứa đáp án A, B, C, D.
   - **Bottom:** Nút "Xác nhận". Khi chọn đáp án và xác nhận, đáp án sẽ đổi màu xanh/đỏ và hiển thị lời giải chi tiết (Hint).
5. **Màn hình Profile:**
   - Hiển thị Avatar, Tổng số điểm kinh nghiệm (XP), radar chart thể hiện độ thành thạo các môn học. Menu Settings, Đăng xuất.

## 4. Navigation Map (Sơ đồ luồng)

Sử dụng `Jetpack Navigation Compose` với logic sau:
- **Root Graph:**
  - `Splash` -> `Login/Register` -> `MainApp`
- **MainApp Graph (Bao bọc bởi BottomNavigationBar):**
  - Route `home`
  - Route `graph`
  - Route `profile`
- **Modal Flows (Ẩn BottomNavigationBar):**
  - Từ `graph` hoặc `home`, navigate tới `quiz/{node_id}`.
  - Từ `quiz/{node_id}`, khi hoàn thành, navigate tới `result/{quiz_id}`.
  - Từ `result/{quiz_id}`, có nút `Back to Home` -> Pop back stack về `home`.
