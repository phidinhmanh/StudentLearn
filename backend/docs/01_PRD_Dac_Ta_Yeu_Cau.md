# Tài liệu Đặc tả Yêu cầu (PRD - Product Requirements Document)

Tài liệu này định nghĩa rõ lý do tại sao hệ thống StudentLearn tồn tại, giá trị cốt lõi mang lại cho người dùng và các yêu cầu chức năng chi tiết.

## 1. Mục tiêu Business (Business Goals)

Hệ thống giáo dục hiện tại thường áp dụng phương pháp tiếp cận "một kích cỡ cho tất cả" (one-size-fits-all), dẫn đến việc học sinh có những "lỗ hổng" kiến thức không được phát hiện kịp thời. Khi học lên các kiến thức nâng cao, những lỗ hổng ở phần nền tảng (prerequisites) khiến học sinh mất gốc và chán nản.

**StudentLearn ra đời để giải quyết vấn đề này thông qua:**
- **Chẩn đoán chính xác:** Sử dụng GraphRAG để biểu diễn kiến thức thành một mạng lưới đồ thị (Knowledge Graph). Bằng cách kiểm tra các node, hệ thống phát hiện chính xác lỗ hổng đang nằm ở đâu.
- **Học tập cá nhân hóa:** Tự động đề xuất lộ trình (Learning Path) học lại các node bị hổng trước khi tiến lên node mới.
- **Nâng cao năng lực tư duy:** Áp dụng Thang độ nhận thức Bloom (Bloom's Taxonomy) để đảm bảo học sinh không chỉ "Nhớ" (Recall) mà có khả năng "Hiểu" (Understanding), "Vận dụng" (Application) và "Phân tích" (Analyze).

## 2. User Personas (Chân dung Người dùng)

### 2.1. Học sinh (Người học - End User)
- **Đặc điểm:** Học sinh THPT (15-18 tuổi), thường xuyên sử dụng smartphone, quen thuộc với các app giải trí có tính tương tác cao, nhưng dễ mất tập trung khi học tập truyền thống.
- **Nỗi đau (Pain points):** Không biết mình đang yếu phần nào; ôn tập dàn trải, tốn thời gian; thiếu động lực học tập hàng ngày.
- **Mục tiêu:** Cải thiện điểm số, hiểu sâu bản chất vấn đề, muốn thấy tiến bộ của bản thân qua các con số và visual sinh động.

### 2.2. Giáo viên (Người quản lý nội dung - Admin User)
- **Đặc điểm:** Giáo viên bộ môn (Toán, Lý, Hóa...), có chuyên môn cao nhưng không phải chuyên gia công nghệ.
- **Nỗi đau:** Tốn quá nhiều thời gian soạn câu hỏi trắc nghiệm, khó theo dõi sát sao điểm yếu của từng học sinh trong lớp 40-50 em.
- **Mục tiêu:** Cần một công cụ chỉ cần upload file tài liệu (PDF, Word) là tự động sinh ra cây kiến thức và ngân hàng câu hỏi để giao cho học sinh.

## 3. User Stories & Acceptance Criteria

### Epic 1: Knowledge Graph & Learning Path
- **User Story 1.1:** Là một học sinh, tôi muốn nhìn thấy sơ đồ tri thức của môn học để biết tổng quan những gì tôi cần học và tôi đang ở đâu.
  - *Acceptance Criteria:* Hệ thống hiển thị đồ thị dạng Node-Edge. Node đã master có màu xanh, node chưa học màu xám, node đang hổng màu đỏ.
- **User Story 1.2:** Là một học sinh, tôi muốn hệ thống chỉ ra chính xác bài tôi cần học tiếp theo dựa trên kết quả bài Quiz.
  - *Acceptance Criteria:* Sau khi làm bài quiz, nếu rớt, hệ thống hiển thị danh sách các Node "Prerequisite" cần học lại.

### Epic 2: Quiz & Assessment
- **User Story 2.1:** Là một học sinh, tôi muốn làm bài kiểm tra trắc nghiệm ngắn để đánh giá năng lực của một khái niệm cụ thể.
  - *Acceptance Criteria:* Hệ thống sinh ra 5 câu hỏi MCQ dựa trên Bloom's Taxonomy. Hỗ trợ hiển thị công thức Toán học (LaTeX).
- **User Story 2.2:** Là một giáo viên, tôi muốn hệ thống tự động sinh câu hỏi tránh mức độ "Học thuộc lòng" (Recall).
  - *Acceptance Criteria:* 100% câu hỏi sinh ra phải ở mức Understanding, Application, hoặc Analyze.

## 4. Kịch bản Meme & Gamification (Tăng tương tác)

Để giữ chân học sinh (Retention rate), hệ thống áp dụng cơ chế Gamification với Mascot là chú chó "Cheems" kết hợp hệ thống "Ngọn lửa tri thức".

### 4.1. Logic "Ngọn lửa tri thức" (Streak System)
- **Định nghĩa:** Streak là số ngày liên tiếp học sinh có tương tác ý nghĩa trên app (Hoàn thành 1 bài Quiz hoặc đọc 1 khái niệm mới).
- **Quy luật:**
  - **Cháy sáng:** Khi hoàn thành mục tiêu ngày, ngọn lửa chuyển sang màu Cam rực rỡ, cộng 1 vào chuỗi Streak.
  - **Yếu dần:** Nếu qua 24h không học, ngọn lửa chuyển sang màu xám/xanh nhạt (cảnh báo).
  - **Tắt ngấm:** Qua 48h không học, Streak reset về 0. Ngọn lửa bị dập tắt bởi một "xô nước".
  - **Freeze Token (Thẻ đóng băng):** Đạt streak 7 ngày sẽ được tặng 1 thẻ "Đóng băng" để bảo vệ streak nếu có lỡ nghỉ 1 ngày.

### 4.2. Trạng thái của Cheems (Mascot)
Cheems xuất hiện ở góc màn hình hoặc trong các popup feedback, trạng thái thay đổi realtime theo performance của học sinh:
- **Cheems Đam mê (On Fire):** 
  - *Kích hoạt:* Khi học sinh đạt chuỗi Streak ≥ 3 ngày, hoặc trả lời đúng 5 câu liên tiếp.
  - *Visual:* Cheems đeo kính râm ("Thug life"), xung quanh có aura lửa cháy.
  - *Dialogue text:* "Tuyệt vời ô trym! Đỉnh của chóp!", "Kiến thức này đã thấm vào máu!".
- **Cheems Trí tuệ (Mastery):**
  - *Kích hoạt:* Khi học sinh đạt mức độ "Master" (Skill level 3) cho một node khó.
  - *Visual:* Cheems đội mũ cử nhân, cầm sách, mắt phát sáng meme "Big Brain".
  - *Dialogue text:* "Giác ngộ rồi!", "Đề thi đại học cũng chỉ đến thế này thôi!".
- **Cheems Suy sụp (Struggling):**
  - *Kích hoạt:* Khi học sinh làm sai 3 câu liên tiếp trong một bài Quiz, hoặc bị rớt Skill level.
  - *Visual:* Cheems ngồi khóc ròng, nước mắt tuôn rơi, ôm một cuốn sách dày.
  - *Dialogue text:* "Não tôi đau quá man...", "Có vẻ chúng ta phải ôn lại kiến thức nền thôi, đừng buồn nhé!".
