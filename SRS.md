ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)
Software Requirements Specification
KnowledgeMap Learning App — v1.0
Chuẩn ISO/IEC/IEEE 29148:2018  |  Giai đoạn: MVP Implementation
Hệ thống
KnowledgeMap Learning App
Phiên bản
1.0 — Sẵn sàng triển khai
Nền tảng
Android (Kotlin + Jetpack Compose)
Đối tượng dùng app
Học sinh THPT — Toán lớp 10
AI engine
Gemini API (câu hỏi) + GraphRAG / Cognee (Knowledge Graph)
Tiêu chuẩn
ISO/IEC/IEEE 29148:2018 · IEEE 1016





1. Giới thiệu
1.1  Mục đích tài liệu
Tài liệu này đặc tả đầy đủ yêu cầu chức năng, yêu cầu phi chức năng và ràng buộc kỹ thuật của KnowledgeMap Learning App — phục vụ trực tiếp giai đoạn implement. Mỗi yêu cầu được viết dưới dạng kiểm chứng được theo chuẩn IEEE 29148.
1.2  Phạm vi hệ thống
Ứng dụng Android giúp học sinh THPT tự xác định lỗ hổng kiến thức theo từng topic trong chương trình và nhận gợi ý lộ trình học cá nhân hóa. Giai đoạn MVP: môn Toán lớp 10, 1 người dùng, local-first. AI pipeline: tài liệu → extract Knowledge Graph (GraphRAG/Cognee) → assessment (Gemini) → recommendation (graph traversal).
1.3  Định nghĩa thuật ngữ

Thuật ngữ
Định nghĩa
Knowledge Graph (KG)
Đồ thị tri thức: node = topic, edge có nhãn (prerequisite / sequenceOf / relatedTo). Đây là cấu trúc dữ liệu trung tâm của hệ thống.
GraphRAG
Retrieval-Augmented Generation kết hợp vector search + graph traversal. Dùng để extract KG từ tài liệu và enrich context cho Gemini.
Cognee
Python SDK open-source tự động xây Knowledge Graph từ văn bản thô. Pipeline: add() → cognify() → search().
Topic
Node trong Knowledge Graph — đơn vị kiến thức nhỏ nhất, tương ứng 1 khái niệm trong chương trình.
Skill Level
Trạng thái thành thạo của 1 topic: 0=Chưa học, 1=Cần ôn, 2=Đang học, 3=Đã vững.
Assessment
Bài quiz 5 câu trắc nghiệm do Gemini API generate, context-aware từ Knowledge Graph.
Recommendation
Danh sách topic ưu tiên gợi ý, tính bằng graph traversal + Skill Level ranking.
Prerequisite edge
Cạnh có hướng trong KG: A → B nghĩa là phải đạt Skill Level ≥ 2 ở A trước khi được gợi ý B.
Cold start
Trạng thái khi user chưa có dữ liệu assessment — hệ thống dùng syllabus structure làm điểm xuất phát.
Local-first
Toàn bộ dữ liệu người dùng lưu trên thiết bị (Room DB). Chỉ gọi mạng khi cần Gemini API.




2. Mô tả tổng quát hệ thống
2.1  Kiến trúc tổng thể
Hệ thống gồm 4 layer chính hoạt động tuần tự:
Document Ingestion Layer  — nhận file tài liệu → chunk → extract entity + relationship bằng Gemini/Cognee → lưu Knowledge Graph vào Room DB
Knowledge Graph Layer  — lưu trữ và query graph (nodes, edges, nhãn quan hệ) — nền tảng cho recommendation
Assessment Layer  — Gemini API generate câu hỏi dựa trên topic node + context từ graph → chấm điểm → update Skill Level
Recommendation Layer  — graph traversal từ current state → xếp hạng topic theo priority rule → trả top 3
2.2  Đặc điểm người dùng
Học sinh THPT lớp 10, 15–16 tuổi, dùng smartphone Android
Không cần hiểu AI hay graph — giao diện hoàn toàn ẩn kỹ thuật
Mục tiêu: tự ôn tập, xác định điểm yếu, chuẩn bị kiểm tra
2.3  Giả định và phụ thuộc
Thiết bị Android ≥ API 26 (Android 8.0), RAM ≥ 2GB
Kết nối internet khi gọi Gemini API — mất mạng thì assessment tạm ngưng, các tính năng khác vẫn chạy offline
Chương trình Toán 10 theo GDPT 2018, bộ sách Kết Nối Tri Thức làm chuẩn Knowledge Map mặc định
Gemini API ổn định — timeout 10 giây; nếu vượt, hiển thị lỗi và cho phép retry



3. Ràng buộc kỹ thuật (Constraints)
Đây là phần quan trọng nhất cho giai đoạn implement. Mỗi ràng buộc là điều kiện cứng — vi phạm sẽ làm hệ thống không chạy đúng.


3.1  Ràng buộc dữ liệu
[CON-D01]  Ràng buộc: Knowledge Graph phải lưu dưới dạng đồ thị có hướng. Mỗi edge BẮT BUỘC có nhãn: prerequisite | sequenceOf | relatedTo. Không lưu dạng list phẳng.
[CON-D02]  Ràng buộc: Skill Level của 1 topic chỉ nhận giá trị nguyên trong tập {0, 1, 2, 3}. Không được lưu float hay string.
[CON-D03]  Ràng buộc: Một topic chỉ được gợi ý khi TẤT CẢ prerequisite edge trỏ vào nó có Skill Level ≥ 2. Vi phạm điều kiện này → không được hiển thị trong Recommendation.
[CON-D04]  Ràng buộc: Kết quả Assessment phải được persist vào Room DB TRƯỚC KHI cập nhật UI. Không được update UI trước khi lưu thành công.
[CON-D05]  Ràng buộc: Knowledge Graph của từng môn học được đóng gói sẵn trong app (JSON asset). Không fetch graph từ server khi dùng lần đầu — đảm bảo hoạt động offline hoàn toàn.

3.2  Ràng buộc API
[CON-A01]  Ràng buộc: Mọi request Gemini API PHẢI có timeout 10 giây. Nếu vượt quá, BẮT BUỘC hiển thị thông báo lỗi — không để app treo vô thời hạn.
[CON-A02]  Ràng buộc: Prompt gửi Gemini PHẢI yêu cầu output JSON hợp lệ và bao gồm: (1) nội dung topic, (2) Skill Level hiện tại của user, (3) prerequisite context từ KG. Thiếu context → câu hỏi không đúng level.
[CON-A03]  Ràng buộc: Gemini API key KHÔNG ĐƯỢC hardcode trong source code. BẮT BUỘC đọc từ BuildConfig hoặc local.properties — không commit key lên Git.
[CON-A04]  Ràng buộc: Mỗi lần gọi Gemini để generate câu hỏi: tối đa 5 câu trắc nghiệm, mỗi câu ≤ 200 token input. Vượt ngưỡng → truncate nội dung topic, không tăng giới hạn.
[CON-A05]  Ràng buộc: Khi parse JSON từ Gemini: BẮT BUỘC validate đủ 4 field mỗi câu (q, opts, correct, explain). Thiếu field → bỏ câu đó, không crash app.

3.3  Ràng buộc Knowledge Graph
[CON-G01]  Ràng buộc: Knowledge Graph PHẢI được xây dựng bằng kỹ thuật GraphRAG (hoặc Cognee SDK). Không được hardcode quan hệ giữa các topic bằng tay — graph phải extract từ tài liệu.
[CON-G02]  Ràng buộc: Mỗi node trong KG PHẢI có ít nhất các field: id (unique), name (tiếng Việt), desc (mô tả ≤ 100 ký tự), difficulty (1|2|3), prereq (mảng id).
[CON-G03]  Ràng buộc: Cạnh prerequisite là có hướng và bắc cầu: nếu A→B và B→C thì A cũng là prerequisite gián tiếp của C. Recommendation phải kiểm tra cả quan hệ trực tiếp lẫn gián tiếp.
[CON-G04]  Ràng buộc: Khi thêm môn học mới: PHẢI có thể import chỉ bằng file JSON graph — không cần sửa code. Cấu trúc JSON cố định, validate trước khi import.

3.4  Ràng buộc bảo mật & privacy
[CON-S01]  Ràng buộc: Dữ liệu học tập (Skill Level, lịch sử assessment) KHÔNG được gửi lên server bất kỳ. Local-first hoàn toàn cho giai đoạn MVP.
[CON-S02]  Ràng buộc: Khi gọi Gemini API, nội dung tài liệu được truncate tối đa 3000 ký tự — không gửi toàn bộ file lên nếu file quá dài.
[CON-S03]  Ràng buộc: App KHÔNG yêu cầu quyền camera, microphone, contacts, location. Chỉ cần INTERNET permission.

3.5  Ràng buộc hiệu năng
[CON-P01]  Ràng buộc: Knowledge Map (từ Room DB) phải load trong ≤ 1 giây trên thiết bị RAM 2GB.
[CON-P02]  Ràng buộc: Recommendation Engine phải trả kết quả trong ≤ 2 giây — KHÔNG gọi API nào, tính offline hoàn toàn.
[CON-P03]  Ràng buộc: App KHÔNG được crash khi Gemini trả về JSON sai format. BẮT BUỘC có try/catch và fallback message.
[CON-P04]  Ràng buộc: Database schema phải có migration path — không được xóa dữ liệu user khi update app version.



4. Yêu cầu chức năng
Quy ước: [FR-XX] = yêu cầu chức năng. Tất cả viết dạng "Hệ thống sẽ..." — mỗi yêu cầu có thể viết test case kiểm chứng Đạt/Không đạt.


4.1  Document Ingestion & Knowledge Graph Builder
Use Case UC-01: Nhập tài liệu và xây Knowledge Graph

Trường
Chi tiết
Tác nhân
Học sinh / Giáo viên
Điều kiện tiên quyết
User đã đăng nhập và đang ở màn hình chọn môn học
Luồng chính
(1) User nhập hoặc paste nội dung tài liệu → (2) Hệ thống chunk văn bản ≤ 3000 ký tự → (3) Gọi Gemini/Cognee API extract danh sách topic + quan hệ → (4) Parse JSON kết quả → (5) Validate đủ field bắt buộc → (6) Lưu Knowledge Graph vào Room DB → (7) Hiển thị Knowledge Map cho user
Luồng lỗi 1
API timeout (>10s) → hiển thị: "Không thể phân tích tài liệu. Kiểm tra kết nối và thử lại."
Luồng lỗi 2
JSON parse fail → retry 1 lần → nếu vẫn lỗi → hiển thị lỗi, không crash
Điều kiện sau
Knowledge Graph được lưu local; Knowledge Map hiển thị với tất cả topic ở Skill Level 0


Yêu cầu chi tiết:
[FR-01]  Hệ thống sẽ nhận văn bản tài liệu (tối đa 10.000 ký tự), tự động chunk và gọi AI extract danh sách topic + quan hệ prerequisite giữa chúng.
[FR-02]  Hệ thống sẽ validate JSON trả về: mỗi topic BẮT BUỘC có đủ id, name, desc, prereq, difficulty — bỏ qua topic thiếu field, không crash.
[FR-03]  Hệ thống sẽ lưu Knowledge Graph vào Room DB với đúng cấu trúc node-edge trong ≤ 3 giây sau khi nhận được response hợp lệ.
[FR-04]  Hệ thống sẽ hỗ trợ import Knowledge Graph từ file JSON sẵn có (default graph của môn Toán 10) khi user không muốn nhập tài liệu mới.

4.2  Knowledge Map — Bản đồ tri thức
[FR-05]  Hệ thống sẽ hiển thị tất cả topic trong Knowledge Graph theo nhóm chapter, load trong ≤ 1 giây từ Room DB.
[FR-06]  Hệ thống sẽ render màu trạng thái cho mỗi topic: xám=Chưa học (0), đỏ=Cần ôn (1), vàng=Đang học (2), xanh=Đã vững (3).
[FR-07]  Hệ thống sẽ hiển thị biểu tượng khóa và tooltip cho topic chưa đủ điều kiện prerequisite — không cho phép bắt đầu Assessment.
[FR-08]  Hệ thống sẽ hiển thị quan hệ prerequisite giữa các topic khi user nhấn vào 1 topic ("Cần học trước: X, Y").
[FR-09]  Hệ thống sẽ cung cấp bộ lọc topic theo Skill Level (Tất cả / Cần ôn / Chưa học / Đang học / Đã vững).
[FR-10]  Hệ thống sẽ hiển thị phần trăm hoàn thành tổng thể của môn học (số topic Skill Level ≥ 2 / tổng topic).

4.3  Assessment — Đánh giá topic
Use Case UC-02: Làm bài kiểm tra 1 topic

Trường
Chi tiết
Tác nhân
Học sinh
Điều kiện tiên quyết
Topic được chọn có Skill Level ≥ 0 và TẤT CẢ prerequisite có Skill Level ≥ 2
Luồng chính
(1) User chọn topic → nhấn "Kiểm tra" → (2) Hệ thống build prompt: topic + context từ KG (prereq đã biết) + Skill Level hiện tại → (3) Gọi Gemini API → (4) Parse 5 câu hỏi JSON → (5) Hiển thị từng câu → (6) User chọn đáp án → hiện giải thích → (7) Sau câu 5: tính điểm → cập nhật Skill Level → lưu DB
Luồng lỗi
API timeout hoặc JSON invalid → hiện thông báo, cho retry — không mất kết quả đã làm
Điều kiện sau
Skill Level topic được cập nhật; kết quả lưu vào bảng assessment_history


[FR-11]  Hệ thống sẽ build prompt Gemini có đủ 3 thành phần: (1) tên topic, (2) mô tả context từ KG, (3) Skill Level hiện tại để điều chỉnh độ khó.
[FR-12]  Hệ thống sẽ nhận và parse đủ 5 câu hỏi từ Gemini trong ≤ 10 giây; mỗi câu có: q (câu hỏi), opts (4 đáp án), correct (index 0–3), explain (giải thích).
[FR-13]  Hệ thống sẽ tính Skill Level mới sau assessment: 0–1 đúng → 1 (Cần ôn); 2–3 đúng → 2 (Đang học); 4–5 đúng → 3 (Đã vững).
[FR-14]  Hệ thống sẽ lưu kết quả assessment (topic_id, score, timestamp, new_skill_level) vào Room DB TRƯỚC KHI cập nhật UI.
[FR-15]  Hệ thống sẽ sau khi user trả lời mỗi câu: hiển thị đáp án đúng + giải thích — không cho phép sửa đáp án đã chọn.
[FR-16]  Hệ thống sẽ nếu user làm sai câu nào, hệ thống đề xuất 1 câu luyện tập tương tự ngay sau khi xem kết quả (optional, nếu còn thời gian).

4.4  Recommendation — Gợi ý lộ trình
Use Case UC-03: Nhận gợi ý topic tiếp theo

Trường
Chi tiết
Tác nhân
Học sinh
Điều kiện tiên quyết
User đã có ít nhất 1 topic với Skill Level > 0
Luồng chính
(1) User mở màn hình chính → (2) Recommendation Engine đọc KG + Skill Level map → (3) Chạy thuật toán ưu tiên (xem FR-17) → (4) Trả top 3 topic kèm lý do → (5) User nhấn vào topic → chuyển sang Assessment
Luồng cold start
Chưa có data → gợi ý topic đầu tiên của chapter 1 theo thứ tự KG
Điều kiện sau
User thấy danh sách cập nhật phản ánh đúng trạng thái Knowledge Map hiện tại


[FR-17]  Hệ thống sẽ tính recommendation theo thứ tự ưu tiên: (1) Skill Level 1 là prerequisite của topic sắp học; (2) Skill Level 0 đã đủ prerequisite; (3) Skill Level 2 chưa ôn lâu nhất — trong ≤ 2 giây, offline.
[FR-18]  Hệ thống sẽ KHÔNG gợi ý topic có bất kỳ prerequisite edge nào trỏ vào mà Skill Level < 2.
[FR-19]  Hệ thống sẽ hiển thị lý do gợi ý cụ thể cho mỗi topic: ví dụ "Kết quả yếu lần trước" hoặc "Tiền đề của chương sắp học".
[FR-20]  Hệ thống sẽ khi user nhấn vào topic được recommend → chuyển thẳng vào màn hình Assessment của topic đó.

4.5  Session Logger — Ghi lại buổi học
[FR-21]  Hệ thống sẽ cho phép user ghi lại buổi học: topic, thời gian bắt đầu/kết thúc, tự đánh giá (Hiểu rõ / Cần ôn lại / Chưa hiểu).
[FR-22]  Hệ thống sẽ cập nhật Skill Level theo tự đánh giá: "Hiểu rõ" → tăng 1 bậc (tối đa 3); "Chưa hiểu" → giảm 1 bậc (tối thiểu 0); "Cần ôn lại" → giữ nguyên.
[FR-23]  Hệ thống sẽ khi Skill Level từ AI (Assessment) mâu thuẫn với tự đánh giá: ưu tiên giá trị THẤP HƠN — tránh overconfidence.
[FR-24]  Hệ thống sẽ lưu toàn bộ lịch sử session không xóa tự động — dùng cho analytics sau này.



5. Yêu cầu phi chức năng

Mã ID
Thuộc tính
Yêu cầu — định lượng cụ thể
Phương pháp kiểm chứng
NFR-01
Hiệu năng — load map
Knowledge Map load ≤ 1 giây trên thiết bị RAM 2GB
Android Profiler: đo 10 lần, tính trung bình
NFR-02
Hiệu năng — recommendation
Recommendation Engine trả kết quả ≤ 2 giây, offline
Unit test: mock KG 30 nodes, đo thời gian xử lý
NFR-03
Hiệu năng — Gemini API
API call hoàn thành ≤ 10 giây trên 4G bình thường
Integration test: 20 lần gọi liên tiếp, đo p95
NFR-04
Độ tin cậy
App không crash ≥ 95% phiên sử dụng bình thường
Monkey test: 1000 event ngẫu nhiên, đếm crash
NFR-05
Offline capability
Tất cả tính năng trừ Assessment hoạt động khi không có mạng
Test: tắt wifi, kiểm tra từng màn hình
NFR-06
Bảo mật — API key
Gemini API key không xuất hiện trong APK decompile
apktool decompile APK, grep key — phải không tìm thấy
NFR-07
Bảo mật — data
Dữ liệu user không gửi lên bất kỳ server nào ngoài Gemini
Network capture: không thấy request nào đến domain lạ
NFR-08
Khả năng mở rộng
Thêm môn học mới bằng file JSON, không sửa code
Thêm Vật lý 10, verify app hiển thị đúng không recompile
NFR-09
UX — onboarding
User mới hoàn thành onboarding + Assessment đầu tiên ≤ 3 phút
Usability test: 5 học sinh, đo thời gian
NFR-10
DB migration
Không mất dữ liệu khi update app version
Upgrade từ v1.0 → v1.1, verify tất cả Skill Level còn nguyên




6. Database Schema (Room DB)
Các bảng bắt buộc cho giai đoạn implement:

6.1  Bảng topic_node
Field
Type
Constraint
Mô tả
id
TEXT
PRIMARY KEY, NOT NULL
Unique ID của topic, dùng trong graph edge
name
TEXT
NOT NULL
Tên topic tiếng Việt
desc
TEXT
NOT NULL, ≤100 chars
Mô tả ngắn
difficulty
INTEGER
NOT NULL, IN (1,2,3)
Độ khó: 1=dễ, 2=TB, 3=khó
chapter
TEXT
NOT NULL
Tên chương chứa topic này
subject
TEXT
NOT NULL, DEFAULT 'toan10'
Môn học — chuẩn bị cho multi-subject
skill_level
INTEGER
NOT NULL, DEFAULT 0, IN (0,1,2,3)
Trạng thái học tập hiện tại
last_assessed
INTEGER
NULLABLE
Unix timestamp của lần assessment gần nhất


6.2  Bảng topic_edge
Field
Type
Constraint
Mô tả
from_id
TEXT
FK → topic_node.id, NOT NULL
Node nguồn (topic phải học trước)
to_id
TEXT
FK → topic_node.id, NOT NULL
Node đích
relation
TEXT
NOT NULL, IN ('prerequisite','sequenceOf','relatedTo')
Loại quan hệ
weight
REAL
DEFAULT 1.0, > 0
Trọng số cạnh — dùng khi có nhiều prerequisite


6.3  Bảng assessment_history
Field
Type
Constraint
Mô tả
id
INTEGER
PRIMARY KEY AUTOINCREMENT


topic_id
TEXT
FK → topic_node.id, NOT NULL
Topic được đánh giá
score
INTEGER
NOT NULL, BETWEEN 0 AND 5
Số câu đúng
skill_before
INTEGER
NOT NULL, IN (0,1,2,3)
Skill Level trước assessment
skill_after
INTEGER
NOT NULL, IN (0,1,2,3)
Skill Level sau assessment
timestamp
INTEGER
NOT NULL
Unix timestamp
source
TEXT
NOT NULL, IN ('gemini','self_report')
Nguồn đánh giá


6.4  Bảng session_log
Field
Type
Constraint
Mô tả
id
INTEGER
PRIMARY KEY AUTOINCREMENT


topic_id
TEXT
FK → topic_node.id, NOT NULL
Topic được học
started_at
INTEGER
NOT NULL
Unix timestamp bắt đầu
ended_at
INTEGER
NULLABLE
Unix timestamp kết thúc
self_rating
INTEGER
NULLABLE, IN (0,1,2)
0=Chưa hiểu, 1=Cần ôn, 2=Hiểu rõ




7. Ma trận kiểm chứng
Mỗi yêu cầu cứng phải có test case trước khi deploy giai đoạn tiếp theo.

Yêu cầu
Mô tả test case
Dữ liệu đầu vào
Kết quả Đạt
CON-D03
Topic B có prereq A; A Skill Level = 1
Knowledge Map với A→B edge
B không xuất hiện trong Recommendation
CON-A01
Gemini timeout
Mock API delay 11 giây
App hiển thị lỗi, không treo
CON-A03
API key không trong APK
Build release APK, decompile
Không tìm thấy key string
CON-A05
Gemini trả JSON thiếu field
Mock response: thiếu field 'explain'
App bỏ câu đó, hiện 4 câu, không crash
FR-13
Tính Skill Level đúng
Submit 5 bộ đáp án (0,1,2,3,4,5 đúng)
Skill Level lần lượt: 0→1→1→2→2→3
FR-18
Không gợi ý topic locked
Topic C cần B (Skill 1), B cần A (Skill 2)
C không xuất hiện trong top 3
FR-23
Ưu tiên Skill Level thấp hơn
AI: Skill 3, User self-report: Skill 1
Skill Level cập nhật thành 1
NFR-01
Knowledge Map load time
30 topic, thiết bị RAM 2GB
Trung bình < 1000ms qua 10 lần đo
NFR-05
Offline mode
Tắt wifi, mở app
Knowledge Map hiển thị; Assessment báo lỗi mạng



Tài liệu này tuân theo ISO/IEC/IEEE 29148:2018. Ký hiệu [FR-XX] = functional requirement; [CON-XX] = constraint cứng; [NFR-XX] = non-functional requirement. Mọi thay đổi yêu cầu phải được cập nhật trong tài liệu này trước khi implement.
