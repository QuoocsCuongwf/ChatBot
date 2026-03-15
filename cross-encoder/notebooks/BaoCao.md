MỤC LỤC































DANH MỤC BẢNG BIỂU, HÌNH ẢNH
 
Hình 3.1. Pipeline tiền xử lý dữ liệu
Hình 3.2. Sơ đồ kiến trúc hệ thống RAG tĩnh

Bảng 4.1. Cấu trúc bộ dữ liệu kiểm thử
Bảng 4.2. So sánh hiệu năng các phương pháp truy xuất cơ sở (Baseline)
Bảng 4.3. Tác động của Cross-Encoder Reranking trên nền bge-m3
Bảng 4.4. Hiệu năng của hệ thống bge-m3 sau quá trình Domain Fine-Tuning
Bảng 4.5. So sánh chiến lược Hard Negative Mining cho việc fine-tuning Cross-Encoder
Bảng 4.6. Ablation Study kỹ thuật truy xuất nâng cao trên nền hệ thống V6




































DANH MỤC CÁC CHỮ VIẾT TẮT


RAG
Retrieval-Augmented Generation
LLM
Large Language Model




































BẢN TÓM TẮT ĐỀ TÀI
Trong bối cảnh cải cách hành chính và tinh giản bộ máy nhà nước tại Việt Nam, mô hình chính quyền địa phương đã được điều chỉnh từ ba cấp (Tỉnh/Thành phố – Quận/Huyện – Xã/Phường) xuống còn hai cấp (Tỉnh/Thành phố – Phường). Sự thay đổi này kéo theo nhiều điều chỉnh về chức năng, nhiệm vụ và quy trình thực hiện thủ tục hành chính. Tuy nhiên, thông tin liên quan đến các thay đổi vẫn còn phân tán trên nhiều cổng thông tin điện tử, văn bản pháp luật và hệ thống dịch vụ công, gây khó khăn cho người dân trong việc tiếp cận và tra cứu.
Đề tài “Xây dựng trợ lý ảo hỏi đáp về chính quyền địa phương hai cấp” được thực hiện nhằm phát triển một hệ thống trợ lý ảo có khả năng tiếp nhận và trả lời tự động các câu hỏi liên quan đến tổ chức, chức năng và thủ tục hành chính trong mô hình mới. Hệ thống được xây dựng dựa trên các kỹ thuật xử lý ngôn ngữ tự nhiên và cơ chế truy xuất thông tin, cho phép tổng hợp và cung cấp câu trả lời nhanh chóng, chính xác.
Kết quả nghiên cứu cho thấy chatbot có khả năng hỗ trợ người dùng tra cứu thông tin hiệu quả, giảm thời gian tìm kiếm và nâng cao khả năng tiếp cận thông tin hành chính. Đề tài góp phần đề xuất một giải pháp ứng dụng trí tuệ nhân tạo trong lĩnh vực hành chính công, phù hợp với định hướng chuyển đổi số của Chính phủ Việt Nam.















PHẦN MỞ ĐẦU
1. Lý do chọn đề tài
Trong bối cảnh cải cách hành chính và tinh giản bộ máy nhà nước, Việt Nam đang triển khai mô hình chính quyền địa phương hai cấp nhằm nâng cao hiệu quả quản lý, giảm tầng nấc trung gian và tối ưu hóa nguồn lực. Theo định hướng của Chính phủ Việt Nam và Bộ Nội vụ, mô hình này tinh giản từ hệ thống ba cấp (Tỉnh/Thành phố – Quận/Huyện – Xã/Phường) xuống còn hai cấp (Tỉnh/Thành phố – Phường).
Việc thay đổi cấu trúc hành chính kéo theo nhiều điều chỉnh về chức năng, nhiệm vụ, thẩm quyền và quy trình giải quyết thủ tục hành chính. Tuy nhiên, trên thực tế, thông tin liên quan đến các thay đổi này còn phân tán trên nhiều website khác nhau như cổng thông tin điện tử của các địa phương, các văn bản pháp luật, và hệ thống dịch vụ công trực tuyến. Điều này gây khó khăn cho người dân trong việc tra cứu, cập nhật và hiểu đúng quy định mới.
Mặc dù Cổng Dịch vụ công Quốc gia đã cung cấp nhiều tiện ích tra cứu, nhưng người dân vẫn cần một công cụ hỗ trợ tương tác tự nhiên, dễ sử dụng và có khả năng tổng hợp thông tin nhanh chóng.
Trong bối cảnh chuyển đổi số quốc gia và sự phát triển mạnh mẽ của trí tuệ nhân tạo, việc xây dựng một hệ thống chatbot hỏi đáp tự động về mô hình chính quyền địa phương hai cấp là một giải pháp thiết thực. Trợ lý ảo có thể hỗ trợ người dân tiếp cận thông tin chính xác, kịp thời, góp phần nâng cao hiệu quả cải cách hành chính và thúc đẩy quá trình chuyển đổi số trong khu vực công.
Vì những lý do trên, đề tài “Xây dựng trợ lý ảo hỏi đáp về chính quyền địa phương hai cấp” được lựa chọn nghiên cứu và triển khai.
2. Lịch sử nghiên cứu vấn đề
2.1. Các nghiên cứu về tổ chức bộ máy và mô hình chính quyền đô thị (hai cấp) 
Chủ trương tinh gọn bộ máy và xây dựng chính quyền đô thị (mô hình hai cấp) đã và đang thu hút sự quan tâm của nhiều nhà nghiên cứu. Tác giả Diệp Văn Sơn (2020) trên Tạp chí Quản lý Nhà nước khi nghiên cứu thực tiễn quản lý đã phân tích các phương án thí điểm mô hình hai cấp chính quyền (thành phố và quận) tại Hà Nội, chỉ ra yêu cầu bức thiết phải phân định lại chức năng giải quyết thủ tục hành chính khi không tổ chức HĐND cấp phường [1]. Gần đây, tác giả Đặng Đình Thái (2024) tiếp tục nhấn mạnh việc hoàn thiện chính sách xây dựng chính quyền đô thị cần gắn liền với cơ chế phân cấp, phân quyền và đổi mới phương thức quản lý [2]. Các công trình này khẳng định: tinh gọn bộ máy là tất yếu, nhưng phải đi kèm với công cụ hỗ trợ để đảm bảo thông tin thông suốt và quyền lợi của người dân trong việc tiếp cận dịch vụ hành chính.
2.2. Các nghiên cứu về mức độ hài lòng đối với dịch vụ công trực tuyến.
Về công tác cung cấp dịch vụ hành chính công, các nghiên cứu tập trung vào trải nghiệm của người dân trên các nền tảng số. Nghiên cứu của nhóm tác giả Phạm Thị Ngọc Huệ và cộng sự (2024) công bố trên Tạp chí Khoa học Đại học Bạc Liêu về mức độ hài lòng tại tỉnh Bình Phước đã chỉ ra rằng: tính đáp ứng, quy trình minh bạch và sự tin cậy là các yếu tố then chốt; đồng thời đề xuất ứng dụng trí tuệ nhân tạo để nâng cao tính bảo mật và hiệu quả dịch vụ [3]. Một nghiên cứu khác trên Tạp chí Công Thương (2020) cũng chỉ ra hạn chế của hệ thống hiện tại là quy trình tiếp cận còn phức tạp, đòi hỏi phải tối ưu hóa công nghệ để giảm rào cản tra cứu thủ tục [4].
2.3. Ứng dụng Trí tuệ nhân tạo (AI) và Chatbot trong dịch vụ hành chính công.
 Trên thực tế, việc đưa AI vào hỗ trợ dịch vụ công đã bước đầu được triển khai. Từ giữa năm 2024, UBND tỉnh Thanh Hóa đã tích hợp trợ lý ảo Chatbot AI trên Cổng Dịch vụ công (dichvucong.thanhhoa.gov.vn) để hỗ trợ người dân và doanh nghiệp [5]. Đáng chú ý, sáng kiến "Dịch vụ công AI" (DVC AI) do Chương trình Phát triển Liên Hợp Quốc (UNDP) và Viện IPS triển khai cuối năm 2024 đã cung cấp công cụ hướng dẫn từng bước cho công dân thực hiện thủ tục hành chính, xuất phát từ thực trạng các hệ thống hiện hữu đang quá sức tra cứu đối với người dùng phổ thông [6]. Mới đây nhất, vào tháng 6/2025, Bộ Xây dựng cũng đã chính thức đưa vào hoạt động "Nhân viên AI" (Tổng đài 19001007 và Chatbot đa kênh) để tự động hóa việc hướng dẫn thủ tục, cho thấy xu hướng tất yếu của công nghệ này [7].
2.4. Đánh giá chung và khoảng trống nghiên cứu.
 Tổng quan các tài liệu cho thấy: (1) Nền tảng pháp lý về mô hình chính quyền hai cấp đang được hoàn thiện; (2) Có sự thừa nhận rộng rãi về hạn chế của các nền tảng tra cứu thủ tục truyền thống; và (3) AI bắt đầu được ứng dụng vào dịch vụ hành chính nhưng chủ yếu là các chatbot hỏi đáp tổng đài cơ bản. Tuy nhiên, vẫn tồn tại một khoảng trống nghiên cứu (Research Gap): Chưa có hệ thống chuyên biệt nào ứng dụng các mô hình ngôn ngữ lớn (LLM) để tổng hợp, suy luận và giải đáp cụ thể các kiến thức pháp lý và thủ tục hành chính liên quan đặc thù đến mô hình chính quyền địa phương hai cấp. Đề tài này được thực hiện nhằm lấp đầy khoảng trống đó.


3. Mục đích và nhiệm vụ nghiên cứu.
Mục đích của đề tài là xây dựng một hệ thống chatbot có khả năng tiếp nhận và trả lời tự động các câu hỏi liên quan đến mô hình chính quyền địa phương hai cấp tại Việt Nam, qua đó hỗ trợ người dân tiếp cận thông tin hành chính một cách thuận tiện, nhanh chóng và chính xác hơn. Trong bối cảnh cải cách hành chính và chuyển đổi số đang được đẩy mạnh theo định hướng của Chính phủ Việt Nam, việc ứng dụng trí tuệ nhân tạo để hỗ trợ tra cứu và giải đáp thông tin hành chính mang ý nghĩa thực tiễn rõ rệt.
Để đạt được mục đích trên, đề tài tập trung thực hiện các nhiệm vụ chính bao gồm: nghiên cứu cơ sở pháp lý và tổ chức của mô hình chính quyền địa phương hai cấp; khảo sát nhu cầu tra cứu thông tin của người dân; thiết kế kiến trúc hệ thống chatbot phù hợp với đặc thù lĩnh vực hành chính công; xây dựng và chuẩn hóa cơ sở tri thức từ các nguồn chính thống; triển khai hệ thống hỏi đáp dựa trên kỹ thuật xử lý ngôn ngữ tự nhiên; và tiến hành đánh giá hiệu quả hoạt động của hệ thống thông qua các tiêu chí cụ thể.

4. Đối tượng và phạm vi nghiên cứu.
Đối tượng nghiên cứu của đề tài bao gồm mô hình tổ chức chính quyền địa phương hai cấp tại Việt Nam và các kỹ thuật xây dựng hệ thống chatbot trong bài toán hỏi đáp tri thức hành chính. Đồng thời, đề tài cũng xem xét cách thức tổ chức và cung cấp thông tin trên các nền tảng dịch vụ công hiện nay để làm cơ sở phân tích và thiết kế giải pháp phù hợp.
Về phạm vi nghiên cứu, đề tài tập trung vào việc xây dựng hệ thống chatbot ở mức độ thử nghiệm nhằm giải đáp các câu hỏi liên quan đến cơ cấu tổ chức, chức năng, nhiệm vụ và một số thủ tục hành chính cơ bản trong mô hình chính quyền địa phương hai cấp. Đề tài không bao gồm việc xử lý hồ sơ hành chính thực tế, không tích hợp hệ thống xác thực công dân và không triển khai trực tiếp trên hạ tầng chính thức của Cổng Dịch vụ công Quốc gia. Hệ thống được xây dựng với mục tiêu nghiên cứu và đánh giá tính khả thi của giải pháp công nghệ.

5. Phương pháp nghiên cứu.
Đề tài được thực hiện dựa trên sự kết hợp của nhiều phương pháp nghiên cứu khác nhau nhằm đảm bảo tính khoa học và tính khả thi của giải pháp công nghệ đề xuất. Trước hết, phương pháp nghiên cứu tài liệu được sử dụng để thu thập, phân tích và tổng hợp các văn bản quy phạm pháp luật, nghị quyết, bài báo khoa học và tài liệu liên quan đến mô hình chính quyền địa phương hai cấp, cũng như xu hướng ứng dụng trí tuệ nhân tạo trong hành chính công. Quá trình này không chỉ tạo cơ sở lý luận vững chắc mà còn trực tiếp phục vụ việc xây dựng, bóc tách và chuẩn hóa tập dữ liệu đầu vào (cơ sở tri thức) cho hệ thống máy học.
Bên cạnh đó, phương pháp phân tích và thiết kế hệ thống được áp dụng để xây dựng kiến trúc tổng thể của chatbot, xác định các thành phần cốt lõi và luồng xử lý thông tin, đặc biệt là kiến trúc tích hợp mô hình ngôn ngữ lớn (LLM) và kỹ thuật Sinh văn bản tăng cường truy xuất (RAG). Sau khi hoàn thiện thiết kế, hệ thống được triển khai và đánh giá thông qua phương pháp thực nghiệm mô hình. Các tiêu chí đánh giá tập trung vào độ chính xác trong việc truy xuất ngữ nghĩa từ cơ sở dữ liệu vector, tính tự nhiên và tính xác thực của câu trả lời, cũng như thời gian phản hồi và mức độ phù hợp với nhu cầu tra cứu thông tin của người dùng. Việc kết hợp hài hòa giữa đánh giá định lượng (đo lường các chỉ số hiệu suất của mô hình) và định tính (trải nghiệm thực tế của người dùng) giúp đảm bảo tính khách quan, đa chiều và toàn diện trong toàn bộ quá trình nghiên cứu.
6. Những đóng góp mới của đề tài
Đề tài mang lại những đóng góp cụ thể trên cả hai phương diện lý luận và thực tiễn ứng dụng. Về mặt chuyên môn hành chính, nghiên cứu đã tổng hợp và chuẩn hóa thành công một cơ sở tri thức chuyên biệt phục vụ lĩnh vực chính quyền địa phương hai cấp – một chủ đề có tính đặc thù cao và chưa được khai thác sâu dưới góc độ ứng dụng công nghệ. Việc bóc tách và chuyển đổi dữ liệu phi cấu trúc từ các văn bản quy phạm pháp luật thành định dạng phù hợp cho hệ thống máy học đã tạo ra nguồn học liệu có giá trị cho các nền tảng chính phủ điện tử.
Về mặt công nghệ, đóng góp nổi bật của đề tài là việc thử nghiệm và tối ưu hóa kiến trúc Sinh văn bản tăng cường truy xuất (Retrieval-Augmented Generation - RAG) kết hợp với mô hình ngôn ngữ lớn (LLM) trong một ngữ cảnh pháp lý hẹp. Thay vì sử dụng phương pháp truy vấn từ khóa truyền thống hay các kịch bản hỏi đáp cố định (rule-based), hệ thống đề xuất ứng dụng kỹ thuật nhúng từ (text embedding) và tìm kiếm ngữ nghĩa (semantic search) qua cơ sở dữ liệu vector. Điều này giúp chatbot không chỉ hiểu đúng ý định của người dùng mà còn truy xuất chính xác các điều luật liên quan, từ đó sinh ra câu trả lời tự nhiên, có tính biện luận và giảm thiểu tình trạng "ảo giác" (hallucination) của AI. Kết quả thực nghiệm của đề tài cung cấp một mô hình tham chiếu đáng tin cậy cho việc phát triển các trợ lý ảo pháp lý trong khu vực công.
7. Cấu trúc của đề tài
Chương 1: Cơ sở lý luận và tổng quan nghiên cứu. Trình bày cơ sở lý luận về mô hình chính quyền địa phương hai cấp tại Việt Nam, phân tích các cơ sở pháp lý liên quan và tổng quan các nghiên cứu trước đây về mô hình chính quyền đô thị, dịch vụ công trực tuyến và ứng dụng Trí tuệ nhân tạo (AI)/Chatbot trong lĩnh vực hành chính công.
Chương 2: Phân tích bài toán và yêu cầu hệ thống. Phân tích thực trạng tra cứu thông tin hành chính hiện nay, xác định rõ các yêu cầu chức năng và phi chức năng của hệ thống trợ lý ảo, và mô hình hoá bài toán hỏi đáp tri thức hành chính theo kiến trúc đường ống (pipeline).
Chương 3: Thiết kế và triển khai hệ thống. Trình bày chi tiết việc lựa chọn công nghệ, mô hình, kiến trúc tổng quan của hệ thống (dựa trên RAG), quy trình tiền xử lý dữ liệu (OCR, chuẩn hóa, phân mảnh ngữ nghĩa) và xây dựng cơ sở tri thức, bao gồm mô hình nhúng văn bản và cơ sở dữ liệu vector.
Chương 4: Kết quả thực nghiệm và đánh giá. Trình bày kết quả thực nghiệm định lượng, so sánh năng lực truy xuất giữa các mô hình tiêu biểu (bge-m3, multilingual-e5-base, Legal_hf), đánh giá giới hạn của kiến trúc Cross-Encoder (PhoBERT) và các kỹ thuật RAG nâng cao, qua đó rút ra kết luận thực tiễn định hướng phát triển tổng thể.









Chương 1. Cơ sở lý luận và tổng quan nghiên cứu.
1.1. Mô hình chính quyền địa phương 2 cấp tại Việt Nam.
1.1.1. Cơ sở pháp lý và định hướng cải cách hành chính
Hệ thống hành chính nhà nước tại Việt Nam đang bước vào một giai đoạn chuyển mình mang tính lịch sử, đánh dấu bằng sự thay đổi tư duy quản trị từ trung ương đến địa phương. Nền tảng pháp lý cốt lõi cho tiến trình này là sự ra đời của Luật Tổ chức chính quyền địa phương số 72/2025/QH15, chính thức có hiệu lực thi hành từ ngày 16/06/2025 [8]. Đạo luật này không chỉ đơn thuần là một sự điều chỉnh về mặt kỹ thuật lập pháp, mà thực chất là một cuộc "đại phẫu" tinh gọn bộ máy mang tính đột phá. Lần đầu tiên, hệ thống quản lý nhà nước chính thức từ bỏ mô hình ba cấp hành chính truyền thống (tỉnh - huyện - xã) vốn đã tồn tại nhiều thập kỷ, để chuyển đổi sang cấu trúc tinh gọn với hai cấp chính quyền cốt lõi là cấp tỉnh và cấp xã.
Sự chuyển dịch mang tính bước ngoặt này đồng nghĩa với việc cấp huyện sẽ không còn tồn tại với tư cách là một cấp chính quyền địa phương có đầy đủ các thiết chế lập pháp và hành pháp (Hội đồng nhân dân và Ủy ban nhân dân) như giai đoạn trước. Thay vào đó, bộ máy sẽ được tái cấu trúc theo hướng phẳng hóa, triệt tiêu các khâu trung gian rườm rà. Định hướng cải cách này nhằm giải quyết tận gốc rễ tình trạng chồng chéo về chức năng, thẩm quyền giữa các cấp, đồng thời rút ngắn tối đa quy trình ra quyết định, đảm bảo các chính sách và chỉ đạo từ trung ương hoặc cấp tỉnh được truyền đạt và thực thi trực tiếp, xuyên suốt xuống tận cơ sở.
Để đánh giá sát sao tiến độ và cụ thể hóa lộ trình triển khai cơ chế mới mẻ này, Chính phủ đã kịp thời ban hành Nghị quyết số 268/NQ-CP ngày 31/08/2025. Văn bản này mang ý nghĩa định hướng chiến lược sâu sắc, chính thức nhìn nhận quá trình cấu trúc lại này không chỉ là một nhiệm vụ hành chính thông thường, mà là một "cuộc cách mạng tổ chức bộ máy" toàn diện [9]. Qua lăng kính của Nghị quyết, việc "sắp xếp lại giang sơn" trên phương diện hành chính là giải pháp tiên quyết để phá bỏ sức ì của cơ chế cũ, kiến tạo một không gian phát triển thông thoáng và hiệu quả hơn. Đây được xem là động lực thể chế to lớn, tạo ra khí thế mới và bệ phóng vững chắc để đất nước tự tin bước vào kỷ nguyên vươn mình của dân tộc trong bối cảnh chuyển đổi số và hội nhập toàn cầu.
1.1.2. Thay đổi về chức năng, nhiệm vụ và quy trình thủ tục hành chính
Sự chuyển đổi sang mô hình chính quyền địa phương hai cấp mang theo những thay đổi căn bản về chức năng, nhiệm vụ và quy trình vận hành của toàn bộ hệ thống hành chính nhà nước. Trọng tâm của sự dịch chuyển này là nguyên tắc đẩy mạnh phân cấp, phân quyền, qua đó trao quyền tự chủ thực chất và đề cao trách nhiệm giải trình cho tuyến cơ sở. Theo định hướng mới, Chủ tịch Ủy ban nhân dân cấp tỉnh và cấp xã được giao thẩm quyền trực tiếp, toàn diện trong việc chỉ đạo, điều hành và giải quyết các thủ tục hành chính (TTHC). Sự thay đổi này nhằm mục tiêu cắt giảm tối đa các khâu trung gian, rút ngắn thời gian xử lý hồ sơ và kiên quyết ngăn chặn tình trạng đùn đẩy trách nhiệm, đình trệ hay ùn tắc kéo dài gây ảnh hưởng tiêu cực đến đời sống người dân và hoạt động của doanh nghiệp [8].
Điểm đột phá đáng chú ý nhất trong cấu trúc vận hành mới được thể hiện rõ nét tại các đô thị lớn như Hà Nội, Đà Nẵng và Thành phố Hồ Chí Minh. Tại các địa bàn trọng điểm này, cấp phường chính thức không tổ chức Hội đồng nhân dân, chuyển đổi sang cấu trúc bộ máy hành chính hoạt động thuần túy theo chế độ thủ trưởng [10]. Sự tinh gọn này giúp bộ máy hành chính linh hoạt và phản ứng nhanh nhạy hơn trước các yêu cầu quản lý đô thị phức tạp. Tuy nhiên, mặt trái của mô hình là áp lực thực thi công vụ tăng vọt khi định mức biên chế công chức bình quân chỉ được duy trì ở mức 15 người/phường [10]. Khối lượng công việc khổng lồ, từ quản lý trật tự đô thị, an sinh xã hội đến việc phải trực tiếp tiếp nhận và xử lý hàng ngàn hồ sơ hành chính mỗi tháng, đang đặt lên vai một đội ngũ nhân sự mỏng một gánh nặng quá lớn, tạo ra nguy cơ quá tải hệ thống.
Đứng trước mâu thuẫn sâu sắc giữa yêu cầu nâng cao chất lượng phục vụ và sự giới hạn nghiêm ngặt về quy mô biên chế, việc số hóa toàn diện quy trình thủ tục hành chính đã trở thành một yêu cầu mang tính sống còn. Quá trình này đòi hỏi phải xóa bỏ triệt để tình trạng phân mảnh thông tin thông qua việc liên thông dữ liệu liền mạch giữa các nền tảng quản lý chuyên ngành, tiêu biểu như hệ thống thông tin hộ tịch và cơ sở dữ liệu đất đai [8]. Chỉ khi các luồng dữ liệu cốt lõi này được đồng bộ hóa và kế thừa chéo, cán bộ công chức mới thực sự được giải phóng khỏi các thao tác tra cứu, nhập liệu thủ công lặp đi lặp lại. Từ đó, bộ máy hành chính tuyến cơ sở mới có đủ năng lực để duy trì hiệu suất hoạt động, đảm bảo tính thông suốt cho cơ chế một cửa liên thông và tạo tiền đề vững chắc cho việc ứng dụng các giải pháp trí tuệ nhân tạo (như hệ thống RAG đề xuất) vào hỗ trợ nghiệp vụ.
1.2. Tổng quan về trợ lý ảo và xử lý ngôn ngữ tự nhiên
1.2.1. Phân loại chatbot: Tiếp cận từ hệ luật đến sinh văn bản
Lịch sử phát triển của các hệ thống đối thoại và chatbot chứng kiến sự tiến hóa qua ba thế hệ công nghệ lõi, mỗi thế hệ đại diện cho một bước nhảy vọt về khả năng xử lý ngôn ngữ tự nhiên (NLP). Thế hệ sơ khai nhất là các chatbot dựa trên tập luật (rule-based), vận hành theo cấu trúc cây quyết định và các kịch bản tĩnh được lập trình sẵn. Dù đảm bảo tính chính xác tuyệt đối trong giới hạn kịch bản, mô hình này lại bộc lộ điểm yếu cốt tử là sự cứng nhắc, hoàn toàn tê liệt trước những biến thể ngôn ngữ tự nhiên, lỗi chính tả hay các truy vấn phức tạp. Để khắc phục hạn chế này, thế hệ thứ hai ra đời dựa trên cơ chế truy xuất (retrieval-based), áp dụng các mô hình học máy và tìm kiếm thông tin để trích xuất câu trả lời phù hợp nhất từ một kho văn bản biên soạn sẵn. Mặc dù linh hoạt hơn, mô hình này vẫn bị giới hạn bởi dung lượng cơ sở dữ liệu và thiếu khả năng tự tổng hợp văn bản. Bước tiến đột phá và hiện đại nhất thuộc về thế hệ chatbot sinh văn bản (generative chatbot), được xây dựng trên nền tảng của các mạng nơ-ron sâu và kiến trúc Transformer. Thay vì trích xuất nguyên văn, hệ thống này có khả năng thấu hiểu ý định cốt lõi của người dùng và tự động sinh ra văn bản phản hồi mới theo từng từ, giúp quá trình giao tiếp trở nên trôi chảy, linh hoạt và tự nhiên như con người.

1.2.2. Mô hình ngôn ngữ lớn (LLM) và nghịch lý khi ứng dụng trong thủ tục hành chính
Sự bùng nổ của các Mô hình ngôn ngữ lớn (LLM) đang tạo ra một cuộc cách mạng thực sự trong dịch vụ hành chính công [20], [22]. Với khả năng thấu hiểu ngữ cảnh sâu sắc, LLM mở ra tiềm năng tự động hóa toàn diện khâu tiếp nhận phản ánh và hỗ trợ công dân tra cứu thủ tục hành chính liên tục 24/7, qua đó giảm tải áp lực khổng lồ cho hệ thống chính quyền cơ sở. Tuy nhiên, việc triển khai nguyên bản (zero-shot) các LLM thuần túy vào lĩnh vực pháp luật lại đối diện với những nghịch lý và rủi ro nghiêm trọng. Rủi ro lớn nhất phải kể đến là hiện tượng "ảo giác thông tin" (hallucination), khi AI có xu hướng sinh ra những câu trả lời trôi chảy nhưng lại sai lệch hoàn toàn về mặt pháp lý, chẳng hạn như tự sáng tác ra một khoản tiền phạt hoặc trích dẫn sai số hiệu văn bản [14]. Bên cạnh đó, các LLM truyền thống còn vướng phải điểm mù về tính thời sự do kiến thức bị đóng băng tại thời điểm huấn luyện, dẫn đến rủi ro tư vấn dựa trên những điều luật đã hết hiệu lực.
Hơn nữa, sự phức tạp của hệ thống ngôn ngữ pháp lý mang tính đặc thù cao cũng là một rào cản lớn khiến các LLM đa dụng dễ diễn giải sai tinh thần luật pháp. Cuối cùng, tính chất "hộp đen" (black-box) của các mô hình này đi ngược lại nguyên tắc minh bạch trong tư vấn pháp luật, bởi chúng không thể cung cấp khả năng truy vết chính xác nguồn gốc thông tin. Chính những điểm nghẽn nội tại này đã đặt ra một yêu cầu bắt buộc: nền tảng AI phục vụ hành chính công không thể chỉ dựa vào khả năng "ghi nhớ" của mô hình ngôn ngữ, mà phải được neo bám chặt chẽ vào cơ sở dữ liệu luật pháp thời gian thực. Điều này đóng vai trò là tiền đề cấp thiết
1.3. Khoản trống nghiên cứu và định hướng tiếp cận của đề tài
Mặc dù Trí tuệ nhân tạo (AI) đã bước đầu tạo ra những dấu ấn nhất định trong việc hỗ trợ các nghiệp vụ pháp lý và dịch vụ hành chính công, nhưng trên thực tế, ứng dụng của chúng tại Việt Nam vẫn còn khá hạn chế và rời rạc. Một khoảng trống nghiên cứu đặc biệt lớn hiện nay là sự thiếu hụt hoàn toàn các hệ thống AI chuyên biệt có khả năng xử lý, phân tích và suy luận sâu sắc các tri thức pháp lý phục vụ riêng cho mô hình chính quyền 2 cấp mới. Sự chuyển đổi mô hình này, được thiết lập dựa trên khung pháp lý mới nhất của Luật số 72/2025/QH15 và Nghị quyết số 268/NQ-CP [8], [9], đòi hỏi một năng lực xử lý thông tin hành chính mang tính đặc thù cao mà các hệ thống hiện hành chưa thể đáp ứng.
Hiện nay, phần lớn các hệ thống chatbot hành chính công đang vận hành chủ yếu dựa trên các quy tắc lập trình sẵn (rule-based) với kịch bản cứng nhắc, hoặc sử dụng các Mô hình Ngôn ngữ Lớn (LLM) dạng hỏi đáp thông thường. Các LLM này thường gặp khó khăn trong việc cập nhật luật mới và rất dễ mắc phải hiện tượng "ảo giác thông tin" (hallucination) – đưa ra thông tin sai lệch hoặc trích dẫn nguồn luật không tồn tại – một rủi ro không thể chấp nhận được trong lĩnh vực pháp lý.
Để lấp đầy khoảng trống này, đề tài định hướng tiếp cận bằng việc ứng dụng kiến trúc tiên tiến Sinh văn bản tăng cường truy xuất (Retrieval-Augmented Generation - RAG). Giải pháp này sẽ tận dụng sức mạnh của các siêu mô hình ngôn ngữ (như `bge-m3` [28]) đã được tinh chỉnh tối ưu cho đa ngôn ngữ và từ vựng pháp lý chuyên ngành. Nhờ thiết lập bộ cơ sở dữ liệu Vector chuẩn xác, hệ thống không chỉ cung cấp câu trả lời có tính tự nhiên, dễ hiểu mà còn đảm bảo trích xuất định danh tới từng điều, khoản, điểm của luật định, phân tách rạch ròi các thẩm quyền dễ nhầm lẫn, giúp loại bỏ tối đa rủi ro ảo giác thông tin và xây dựng niềm tin vững chắc cho công dân.
1.4. Kết luận chương
Chương 1 đã trình bày tổng quan về bối cảnh nghiên cứu và cơ sở thực tiễn của đề tài. Với sự ra đời của Luật Tổ chức chính quyền địa phương số 72/2025/QH15 và Nghị quyết số 268/NQ-CP, việc chuyển đổi sang mô hình chính quyền hai cấp đang đặt ra áp lực khổng lồ về mặt xử lý khối lượng thủ tục hành chính tại tuyến cơ sở. Thông qua việc khảo sát các hệ thống trợ lý ảo hiện hữu, nghiên cứu đã chỉ ra những giới hạn cốt lõi của các chatbot truyền thống (rule-based) cũng như rủi ro "ảo giác thông tin" (hallucination) nghiêm trọng khi áp dụng nguyên bản các Mô hình Ngôn ngữ Lớn (LLM) vào lĩnh vực pháp luật. Từ những phân tích đó, chương này đã khẳng định tính cấp thiết của việc phải nghiên cứu, đề xuất một giải pháp công nghệ mới: Hệ thống Sinh văn bản tăng cường truy xuất (RAG). Đây chính là tiền đề quan trọng để đề tài bước sang Chương 2, tập trung phân tích sâu vào các cơ sở lý thuyết và các mô hình công nghệ lõi sẽ được sử dụng để xây dựng hệ thống.















Chương 2. Phân tích bài toán và yêu cầu hệ thống.
2.1. Thực trạng tra cứu thông tin hành chính hiện nay.
Quá trình chuyển đổi sang mô hình chính quyền hai cấp đánh dấu một bước ngoặt quan trọng trong việc tinh gọn bộ máy nhà nước, song cũng đặt ra những thách thức chưa từng có trong công tác quản lý và vận hành. Trước hết, sự thay đổi này đi kèm với một khối lượng văn bản quy phạm pháp luật mới được ban hành ở mức độ khổng lồ. Chỉ tính riêng trong giai đoạn ngắn từ tháng 06 đến tháng 08 năm 2025, Chính phủ đã liên tục ban hành tới 112 Nghị định và Nghị quyết nhằm tạo hành lang pháp lý cho cơ chế mới [9]. Tốc độ ban hành và số lượng văn bản lớn như vậy tạo ra áp lực cực kỳ nặng nề cho đội ngũ cán bộ trong việc cập nhật, thẩm thấu và áp dụng chính xác các quy định vào thực tiễn.
Trực tiếp gánh vác áp lực thực thi này là tuyến cơ sở. Hiện tại, 9.916 phòng chuyên môn cấp xã trên cả nước đang phải đối phó với một khối lượng công việc khổng lồ, ước tính lên tới 4,8 triệu hồ sơ hành chính các loại. Tình hình càng trở nên căng thẳng hơn khi nguồn nhân lực tại đây đang rơi vào nghịch lý "vừa thừa vừa thiếu" [9]. Nghĩa là, bộ máy có thể thừa nhân sự ở các khâu hành chính truyền thống mang tính thủ công, nhưng lại thiếu hụt trầm trọng đội ngũ cán bộ có năng lực chuyên môn pháp lý chuyên sâu và kỹ năng xử lý công việc trên môi trường số để đáp ứng cường độ làm việc mới.
Hệ lụy tất yếu của tình trạng quá tải và bất cập về nhân sự này là sự sụt giảm trong chất lượng phục vụ công chúng. Người dân hiện vẫn vấp phải nhiều rào cản trong giao dịch với cơ quan nhà nước do các thông tin, hướng dẫn về thủ tục hành chính (TTHC) còn phân tán, thiếu tính hệ thống và khó tiếp cận đầy đủ [18], [19]. Bên cạnh đó, xét về góc độ hạ tầng công nghệ, hệ thống phần mềm giải quyết TTHC (Một cửa điện tử) và các hệ thống chuyên ngành tại nhiều địa phương vẫn đang hoạt động rời rạc. Việc thiếu đồng bộ và chưa liên thông dữ liệu triệt để [9] không chỉ làm chậm trễ tiến độ giải quyết hồ sơ, buộc cán bộ phải nhập liệu thủ công nhiều lần, mà còn gây ra tâm lý bức xúc, mệt mỏi cho cả người dân lẫn cán bộ thực thi công vụ.

2.2. Xác thực yêu cầu chức năng và phi chức năng của hệ thống.
Để giải quyết hiệu quả bài toán hỗ trợ thông tin pháp lý và thủ tục hành chính (TTHC) trong bối cảnh chuyển đổi sang mô hình chính quyền hai cấp, hệ thống AI đề xuất cần đáp ứng nghiêm ngặt các tiêu chuẩn về mặt chức năng và phi chức năng như sau:
2.2.1. Nhóm yêu cầu chức năng
Đây là nhóm các tính năng cốt lõi, quyết định khả năng vận hành và mức độ đáp ứng nghiệp vụ của hệ thống:
Tiếp nhận và xử lý đa ngôn ngữ tự nhiên (Natural Language Understanding - NLU): Hệ thống phải có khả năng tiếp nhận các truy vấn đầu vào dưới dạng ngôn ngữ tự nhiên của công dân. Điều này đòi hỏi năng lực phân tích ý định (intent classification) sắc bén, nhận diện chính xác các thực thể pháp lý (NER - Named Entity Recognition) ngay cả khi người dùng sử dụng ngôn ngữ đời thường, tiếng lóng, hoặc diễn đạt chưa chuẩn xác về thuật ngữ chuyên ngành.
Truy xuất ngữ nghĩa và đối soát pháp lý: Không chỉ dừng lại ở việc tìm kiếm từ khóa, hệ thống phải áp dụng truy xuất theo ngữ cảnh (Semantic Search) trên cơ sở dữ liệu pháp luật. Khi xác định được ý định, AI phải trích xuất chính xác các quy định pháp luật hiện hành tương ứng.
Sinh văn bản và trích dẫn minh bạch (Transparent Generation): Câu trả lời sinh ra phải mạch lạc, dễ hiểu và bắt buộc phải đi kèm với trích dẫn nguồn văn bản cụ thể (ví dụ: điểm a, khoản 2, Điều X của Nghị định Y). Đây là chức năng sống còn để đảm bảo tính pháp lý và ngăn chặn triệt để hiện tượng "ảo giác thông tin" (hallucination) của AI.
Hỗ trợ hỏi đáp chuyên sâu đa lĩnh vực: Hệ thống cần bao phủ các điểm nóng về TTHC mà người dân thường xuyên vướng mắc. Trọng tâm bao gồm: lĩnh vực hộ tịch, quản lý đất đai, và đặc biệt là việc giải đáp các chức năng, nhiệm vụ, thẩm quyền giải quyết công việc của các cơ quan theo cấu trúc tổ chức bộ máy 2 cấp mới [8], giúp định tuyến người dân đến đúng cơ quan có thẩm quyền.
2.2.2. Nhóm yêu cầu phi chức năng
Để hệ thống thực sự đi vào đời sống và được công chúng cũng như cán bộ tin dùng, các yếu tố về chất lượng và hiệu năng sau đây là bắt buộc:
Độ chính xác và tính trung lập tuyệt đối: Trong lĩnh vực hành chính - pháp lý, sai số thông tin có thể dẫn đến những hậu quả nghiêm trọng về quyền lợi của công dân. Do đó, thuật toán phải được tinh chỉnh để ưu tiên sự chính xác (Precision) lên hàng đầu. Đồng thời, các luồng thông tin cung cấp phải đảm bảo tính trung lập, khách quan, không chứa thiên kiến (bias) dưới bất kỳ hình thức nào.
Hiệu năng và độ trễ thấp (Low Latency): Thời gian phản hồi của hệ thống (từ lúc nhận câu hỏi đến khi xuất kết quả) phải diễn ra gần như tức thời. Độ trễ thấp không chỉ tối ưu hóa trải nghiệm người dùng mà còn giúp giảm tải áp lực cho hệ thống trong các khung giờ cao điểm khi có hàng ngàn lượt truy vấn cùng lúc.
Trải nghiệm người dùng (UX) và khả năng tiếp cận (Accessibility): Giao diện tương tác cần được thiết kế theo nguyên tắc tối giản, trực quan và thân thiện. Hệ thống phải dễ dàng sử dụng đối với mọi tầng lớp nhân dân, bao gồm cả những người lớn tuổi hoặc những người ít am hiểu về công nghệ thông tin. Việc tích hợp đa nền tảng (Web, Mobile App, Zalo Mini App...) là yếu tố cần thiết để tối đa hóa điểm chạm với người dân.
Kiến trúc linh hoạt và khả năng mở rộng (Scalability): Bối cảnh pháp lý luôn biến động (minh chứng là hàng trăm văn bản mới ra đời trong thời gian ngắn). Do đó, hệ thống cần một kiến trúc linh hoạt (như RAG) cho phép các kỹ sư hoặc quản trị viên dễ dàng cập nhật, bổ sung các văn bản quy phạm pháp luật mới vào cơ sở dữ liệu vector mà không cần phải tốn kém tài nguyên và thời gian để huấn luyện lại (retrain) toàn bộ mô hình ngôn ngữ gốc.

2.3. Các công nghệ lõi sử dụng
2.3. Các công nghệ lõi sử dụng
2.3.1. Nền tảng truy xuất ngữ nghĩa với mô hình bge-m3 (Bi-encoder Backbone)
Trong kiến trúc của một hệ thống Sinh văn bản tăng cường truy xuất (RAG), năng lực cốt lõi quyết định đến độ chính xác của toàn bộ đường ống là quá trình không gian hóa ngữ nghĩa (semantic embedding). Mục tiêu của giai đoạn này là ánh xạ các chuỗi văn bản đầu vào (từ câu hỏi bình dân của người dùng đến các điều khoản luật pháp phức tạp) thành các tập hợp vector số học trong một không gian liên tục. Để đảm nhận trọng trách này, hệ thống đề xuất lựa chọn mô hình `bge-m3` [28] làm "trái tim" (backbone) cho khối Bi-encoder.
`bge-m3` (BAAI General Embedding Multi-lingual, Multi-task, Multi-granularity) đại diện cho thế hệ mô hình nhúng tiên tiến nhất hiện nay, được phát triển bởi Học viện Trí tuệ Nhân tạo Bắc Kinh (BAAI). Sự ưu việt của mô hình này nằm ở cấu trúc kiến trúc Hybrid hỗ trợ cùng lúc ba phương pháp biểu diễn truy xuất độc lập: Dense Retrieval (Nhúng vector ngữ nghĩa sâu), Sparse Retrieval (Biểu diễn từ vựng thưa dựa trên Lexical Match), và Multi-Vector Retrieval (Biểu diễn ma trận đa vector mô phỏng cơ chế tính điểm của ColBERT). 
Đặc biệt, trong bối cảnh văn bản pháp luật hành chính, `bge-m3` chứng minh năng lực kiểm soát hiện tượng "bất đồng từ vựng" (vocabulary mismatch). Nhờ được luyện tập trước (pre-trained) trên một tập kho ngữ liệu khổng lồ bao trùm hơn 100 ngôn ngữ (bao gồm một lượng lớn dữ liệu tiếng Việt chất lượng cao), không gian vector đa chiều của `m3` có khả năng thấu hiểu sự liên kết tiệm cận giữa ngôn ngữ sinh hoạt ("làm sổ đỏ") với văn phong hành chính ("cấp giấy chứng nhận quyền sử dụng đất") mà không đòi hỏi hệ thống phải ghép nối thuật toán phân giải cơ học. Năng lực bao quát không gian ngôn ngữ dồi dào này cho phép `bge-m3` trở thành một "khung gầm vững chắc" với chỉ số Recall ban đầu (Zero-shot) vượt trội hơn hẳn các mô hình nhúng đơn tuyến khác, mở ra dư địa thênh thang để tiến hành các can thiệp tinh chỉnh miền chuyên sâu (Domain Fine-tuning) sau này.

2.3.2. Các mô hình nhúng bổ trợ và tham chiếu đối sánh
Để gia tăng tính xác thực khách quan cho năng lực truy xuất của `bge-m3`, hệ thống xây dựng cơ chế đối chiếu đan chéo với hai dòng kiến trúc nhúng bổ trợ tiêu biểu:
Thứ nhất, mô hình đa ngôn ngữ `multilingual-e5-base` [29]. Thuộc dòng họ E5 (Text Embeddings by Weakly-Supervised Contrastive Pre-training) do Microsoft phát triển, đây là một mô hình biểu diễn mạnh mẽ được tinh chỉnh trên các bộ dữ liệu cặp câu đa ngôn ngữ vô cùng sắc bén. E5 đóng vai trò làm thước đo cơ sở chuẩn mực (standard baseline) để dóng hàng khả năng chuyển nghĩa xuyên ngôn ngữ.
Thứ hai, mô hình ngữ nghĩa pháp lý hẹp `Legal_hf` [13]. Đây là một phiên bản mô hình được tinh chỉnh đặc thù dành riêng cho các văn bản quản lý nhà nước tiếng Việt trên Hugging Face. Việc đưa Legal_hf vào làm cơ sở phân tích cung cấp một phổ quan sát quý giá: đánh giá độ chênh lệch hiệu năng giữa cơ cấu "đại mô hình đa nhiệm khổng lồ" (như bge-m3) so với "mô hình chuyên biệt quy mô nhỏ" (như Legal_hf) khi xử lý các chuỗi thực thể hành chính mang đậm tính học thuật Hán-Việt đặc thù.

2.3.3. Mô hình tinh chỉnh Cross-Encoder trên nền PhoBERT
Mặc dù Bi-encoder có khả năng kiến tạo ngân hàng vector khổng lồ nhờ cơ chế tiền tính toán (pre-compute) ngoại tuyến, nó lại vướng phải một khiếm khuyết nội tại về mặt giải tích cấu trúc: chỉ có thể tính khoảng cách hình học đơn thuần (Cosine Similarity) mà không thể thấu hiểu hoàn toàn sự bắt chéo mối tương quan giữa từng Token trong câu hỏi (Query) và câu trả lời (Passage). 
Để giải quyết tận gốc nhược điểm này, hệ thống thiết kế một tầng lọc tinh chỉnh thứ cấp (Re-ranking) sử dụng kiến trúc Cross-Encoder (CE). Và để đảm đương vị trí cốt yếu này, `PhoBERT` [12] được chỉ định làm trung tâm xử lý. Là mô hình học sâu đầu tiên được tiền huấn luyện dành riêng cho tiếng Việt (dựa trên giải thuật phân tách giới hạn từ chuẩn xác), PhoBERT sở hữu các tấm màng lọc nhận diện hình thái tiếng Việt cực kì thuần thục. Khi tiếp quản mạng lưới Cross-Encoder, thay vì mã hóa Query và Passage riêng rẽ, PhoBERT sẽ ép hai chuỗi dữ liệu này hợp nhất, qua đó kích hoạt toàn bộ cơ chế Self-Attention đa cực để soi xét kỹ lưỡng mức độ rành mạch giữa các khái niệm hành chính bị nhầm lẫn. Việc ứng dụng PhoBERT vào tầng CE đồng nghĩa với việc đẩy năng lực tách biệt ranh giới nhầm lẫn (Decision Boundary) lên ngưỡng tinh vi nhất. 

2.3.4. Thư viện tìm kiếm vector FAISS và thuật toán lân cận gần nhất (ANN)
Trong quá trình thiết kế và xây dựng kiến trúc RAG cho đề tài, sau khi đã thiết lập được xương sống biểu diễn ngữ nghĩa bằng `bge-m3` và các mô hình phụ trợ, một thách thức kỹ thuật lớn khác đặt ra là cấu trúc mạng lưới tìm kiếm vector. Với mô hình chính quyền hai cấp, cơ sở dữ liệu văn bản pháp luật (bao gồm Luật, Nghị định, Thông tư và các hướng dẫn thủ tục hành chính) khi được cắt nhỏ (chunking) sẽ cấu thành hàng chục ngàn vector.
Nếu áp dụng phương pháp tìm kiếm lân cận gần nhất chính xác (Exact K-Nearest Neighbors - KNN) thông thường, hệ thống sẽ phải tính toán độ tương đồng (ví dụ: khoảng cách Cosine) giữa vector của câu hỏi với từng vector tài liệu có trong cơ sở dữ liệu. Độ phức tạp tính toán của phương pháp này là tuyến tính O(N), với N là số lượng vector. Trong thực tế triển khai, điều này tạo ra một "nút thắt cổ chai" (bottleneck) nghiêm trọng về mặt hiệu năng. Thời gian phản hồi có thể lên tới vài giây cho mỗi câu hỏi, hoàn toàn không đáp ứng được yêu cầu của một hệ thống chatbot hành chính công cần phục vụ nhiều người dân cùng lúc (high concurrency).
Để giải quyết bài toán tối ưu hóa này, đề tài đã quyết định tích hợp FAISS (Facebook AI Similarity Search) vào đường ống hệ thống [26]. FAISS là một thư viện mã nguồn mở do Meta AI phát triển, được viết bằng ngôn ngữ C++ giúp tối ưu hóa tối đa việc quản lý bộ nhớ và tính toán trên các không gian vector nhiều chiều. Điểm cốt lõi khiến FAISS hoạt động cực kỳ nhanh là do nó không thực hiện tìm kiếm vét cạn (exhaustive search), mà sử dụng các thuật toán Tìm kiếm lân cận gần nhất xấp xỉ (Approximate Nearest Neighbor - ANN). Về bản chất, ANN chấp nhận đánh đổi một tỷ lệ sai số vô cùng nhỏ (khoảng 1-2% độ chính xác) để đổi lấy tốc độ truy xuất tăng lên gấp hàng trăm lần.
Trong khuôn khổ đồ án, hệ thống tập trung khai thác hai cấu trúc lập chỉ mục (indexing) mạnh mẽ nhất của FAISS để xử lý tập dữ liệu luật:
Thứ nhất là Chỉ mục tệp nghịch đảo (IndexIVF - Inverted File Index): Thuật toán này sử dụng phương pháp phân cụm K-means để chia toàn bộ không gian vector dữ liệu luật thành nhiều khu vực (gọi là các Voronoi cells). Mỗi khu vực sẽ có một điểm trung tâm (centroid). Thay vì duyệt qua toàn bộ cơ sở dữ liệu, khi người dùng nhập câu hỏi (ví dụ: hỏi về thủ tục làm sổ đỏ), hệ thống chỉ cần tính khoảng cách từ vector câu hỏi đến các điểm trung tâm này. Sau khi tìm được cụm gần nhất (ví dụ: cụm chứa các luật về đất đai), hệ thống mới bắt đầu tìm kiếm chi tiết các văn bản bên trong cụm đó. Kỹ thuật này giúp cắt giảm đi phần lớn không gian tìm kiếm không cần thiết.
Thứ hai là cấu trúc Đồ thị HNSW (Hierarchical Navigable Small World): Để tăng tốc độ tìm kiếm hơn nữa, FAISS hỗ trợ lưu trữ vector dưới dạng đồ thị đa tầng. Ở các tầng trên cùng của đồ thị HNSW, các node (đại diện cho vector) được kết nối thưa thớt với nhau bằng các "bước nhảy" rất dài. Càng xuống các tầng dưới, số lượng node càng nhiều và kết nối càng chằng chịt, chi tiết hơn. Khi truy vấn đi vào, thuật toán sẽ đi từ tầng cao nhất để nhanh chóng định vị khu vực dữ liệu tương đồng, sau đó đi dần xuống các tầng thấp để lấy kết quả chính xác nhất. Thuật toán này giúp giảm độ phức tạp tìm kiếm xuống mức logarit O(log N).
Nhìn chung, việc lựa chọn và cấu hình chuẩn xác thư viện FAISS đóng vai trò như một "động cơ" đắc lực cho module truy xuất. Nó giúp hệ thống RAG của đồ án có thể quét qua hàng triệu điều khoản pháp luật và trả về Top-k đoạn văn bản phù hợp nhất chỉ trong vòng vài chục mili-giây (ms). Điều này không chỉ giúp tiết kiệm tài nguyên máy chủ mà còn đảm bảo trải nghiệm tương tác mượt mà, thời gian thực cho người dân khi sử dụng trợ lý ảo.
2.4. Mô hình hoá bài toán hỏi đáp tri thức hành chính
Bài toán hỏi đáp pháp lý tự động phục vụ chính quyền hai cấp được thiết kế theo dạng một đường ống (pipeline) Xử lý Ngôn ngữ Tự nhiên xuyên suốt. Mục tiêu tổng quát của hệ thống là tiếp nhận câu hỏi của người dùng, đối chiếu với một tập hợp cơ sở tri thức hành chính đã được phân mảnh, từ đó tổng hợp và sinh ra một câu trả lời chính xác nhất.
Đường ống này được giải quyết thông qua ba pha xử lý tuyến tính và liên kết chặt chẽ với nhau:
Pha 1: Không gian hóa ngữ nghĩa (Semantic Embedding)
Ngay khi tiếp nhận truy vấn, hệ thống không xử lý trực tiếp trên mặt chữ mà sử dụng một mô hình nhúng (embedding model) để chuyển đổi câu hỏi và các mảnh tài liệu vào cùng một không gian vector liên tục.
Để vượt qua rào cản của ngôn ngữ pháp lý tiếng Việt (đặc thù nhiều từ Hán-Việt, cấu trúc câu phức), hệ thống ưu tiên sử dụng siêu kiến trúc `bge-m3` [28] với cấu hình tinh chỉnh làm trọng tâm, song song với việc phân tích đo lường bổ trợ bằng các mô hình chuẩn hóa như `multilingual-e5-base` [29] hay `Legal_hf` [13]. Các mạng lưới này bảo toàn tối đa ý nghĩa gốc của văn bản, ép các khái niệm pháp lý đồng nghĩa hội tụ xung quanh một trường vector trong không gian không gian toán học.

Pha 2: Truy xuất và xếp hạng ngữ nghĩa (Semantic Retrieval & Re-ranking)
Để giải quyết bài toán tìm kiếm trên không gian dữ liệu khổng lồ và xử lý tình trạng chồng chéo thông tin pháp lý (ví dụ: một thủ tục hành chính bị chi phối bởi nhiều văn bản luật khác nhau), hệ thống áp dụng các thuật toán tìm kiếm lân cận gần nhất (K-Nearest Neighbors).
Hệ thống tiến hành tính toán mức độ tương đồng giữa vector câu hỏi và toàn bộ tập vector tài liệu thông qua các phép đo khoảng cách hình học (điển hình là độ tương đồng Cosine). Qua quá trình đối chiếu này, hệ thống sẽ tự động lọc và trích xuất ra một tập hợp các đoạn tài liệu có điểm số tương đồng cao nhất. Để tăng cường độ chính xác trước khi đưa vào mô hình ngôn ngữ, một màng lọc xếp hạng lại (Re-ranking) có thể được bổ sung nhằm đánh giá sâu hơn sự liên kết logic, qua đó loại bỏ các mảnh tài liệu nhiễu.
Pha 3: Sinh đáp án tăng cường ngữ cảnh (Context-driven Generation)
Ở chặng cuối của đường ống, một Mô hình Ngôn ngữ Lớn (LLM) đóng vai trò là bộ sinh văn bản. Lúc này, tập hợp tài liệu chuẩn xác nhất vừa được truy xuất sẽ được đưa trực tiếp vào cửa sổ ngữ cảnh (context window) của LLM cùng với truy vấn gốc của người dùng.
Mục tiêu của quá trình sinh văn bản là dự đoán và tạo ra chuỗi từ vựng đầu ra có mức độ phù hợp cao nhất, dựa trên điều kiện tiên quyết là ngữ cảnh luật pháp vừa được cung cấp. Bằng cách ràng buộc hoàn toàn nội dung đầu ra vào tập ngữ cảnh cứng này, hệ thống đóng băng khả năng "sáng tạo tự do" của LLM. Kết quả là đáp án sinh ra vừa duy trì được sự lưu loát của ngôn ngữ tự nhiên, vừa đảm bảo tính chính xác tuyệt đối và có khả năng trích dẫn ngược lại nguồn luật pháp quy định.
2.5 Kết luận chương
Trong Chương 2, đồ án đã đi sâu vào việc mô hình hóa bài toán và chuẩn hóa toàn bộ các điểm nổ kỹ thuật trong đường ống RAG phục vụ giải đáp hành chính. Nghiên cứu tập trung loại trừ các khiếm khuyết nguyên bản của LLM, lập luận sắc bén để lựa chọn và định hình mô hình đa ngôn ngữ `bge-m3` trở thành nòng cốt biểu diễn (Bi-encoder Backbone). Song song đó, vai trò của mô hình nhúng phụ trợ và bộ tái xếp hạng Cross-Encoder sử dụng nhân `PhoBERT` cũng được giới thiệu nhằm củng cố tính chặt chẽ trong khâu phân giải ranh giới hành chính phức tạp. Bên cạnh đó, các thuật toán không gian tiệm cận xấp xỉ cấu trúc IVF và đồ thị HNSW thông qua thư viện FAISS cũng được mổ xẻ để gia cố hiệu năng truy xuất ở quy mô lớn. Nền tảng cấu trúc vững chãi này là tiền đề trực tiếp để đề tài bước vào công đoạn thực hành chi tiết ở Chương 3, thiết kế kỹ lưỡng quá trình tiền xử lý và xây dựng biểu đồ luồng cho đường ống.

Chương 3. Thiết kế và triển khai hệ thống.
3.1. Lựa chọn công nghệ và mô hình.
3.1.1. Tiền xử lý dữ liệu.
Nguồn dữ liệu đầu vào phục vụ xây dựng cơ sở tri thức cho hệ thống chủ yếu bao gồm các văn bản quy phạm pháp luật, nghị quyết, thông tư và tài liệu hướng dẫn liên quan đến mô hình chính quyền địa phương hai cấp. Đa phần các tài liệu này hiện được lưu trữ dưới dạng tệp PDF (bản quét ảnh) hoặc bản sao số hóa từ văn bản giấy, khiến nội dung tồn tại ở dạng dữ liệu phi cấu trúc thay vì văn bản máy có thể đọc hiểu (machine-readable). Chính vì vậy, giai đoạn tiền xử lý dữ liệu đóng vai trò tiên quyết nhằm chuyển đổi các nguồn tin này thành định dạng chuẩn hóa, đảm bảo tính chính xác và toàn vẹn trước khi đưa vào không gian vector của hệ thống RAG.

Hình 3.1. Pipeline tiền xử lý dữ liệu
Để giải quyết bài toán nhận dạng văn bản tiếng Việt với độ phức tạp cao, nhóm nghiên cứu đề xuất chiến lược kết hợp đa mô hình nhận dạng ký tự quang học (OCR). Cụ thể, hệ thống sử dụng PaddleOCR [23] làm công cụ nền tảng nhờ khả năng vượt trội trong việc xử lý tiếng Việt có dấu và bóc tách tốt các bố cục văn bản hành chính phức tạp như bảng biểu hay các cột nội dung song song. Bên cạnh đó, mô hình VietOCR [24] được tích hợp như một lớp bổ trợ nhằm xử lý các trường hợp tài liệu có chất lượng hình ảnh thấp, bị nhiễu hoặc sử dụng các phông chữ cũ đặc thù thường gặp trong các văn bản lưu trữ lịch sử. Việc phối hợp hai mô hình này cho phép hệ thống thực hiện cơ chế đối chiếu chéo (cross-validation), từ đó phát hiện và hiệu chỉnh các sai lệch ký tự, tối ưu hóa độ chính xác tổng thể.
Tiếp nối quá trình số hóa, dữ liệu văn bản thô sẽ trải qua quy trình làm sạch và chuẩn hóa dựa trên các kỹ thuật xử lý ngôn ngữ tự nhiên tiên tiến, tham khảo định hướng từ nền tảng ProtonX [25]. Các thao tác xử lý bao gồm: loại bỏ các ký tự nhiễu sinh ra do lỗi quét ảnh, thống nhất toàn bộ văn bản về bảng mã Unicode (UTF-8) dựng sẵn, và đặc biệt là kỹ thuật tái cấu trúc văn bản (text restructuring) để xử lý lỗi ngắt dòng sai định dạng – một vấn đề phổ biến trong OCR. Cuối cùng, nội dung được phân tách và định danh lại theo cấu trúc cây phân cấp (Chương, Mục, Điều, Khoản). Quá trình tiền xử lý chặt chẽ này là yếu tố then chốt đối với bài toán pháp lý – hành chính, nơi mỗi từ ngữ đều mang tính quy phạm cao; việc đảm bảo dữ liệu sạch sẽ giúp ngăn chặn hiện tượng mô hình ngôn ngữ lớn sinh ra các câu trả lời sai lệch ngữ cảnh hoặc gặp lỗi "ảo giác" (hallucination) khi truy xuất thông tin.
3.1.2. Mô hình nhúng văn bản.
Trong kiến trúc hệ thống RAG, chất lượng của vector nhúng quyết định trực tiếp đến khả năng truy xuất chính xác các văn bản pháp luật. Để tối ưu hóa hiệu năng cho dữ liệu tiếng Việt chuyên ngành, nghiên cứu đề xuất tiến hành khảo sát và đánh giá thực nghiệm đối sánh giữa ba dòng mô hình ngôn ngữ tiêu biểu hiện nay: multilingual-e5-base, Legal_hf (Vietnam_legal_embeddings) và bge-m3.
Mô hình multilingual-e5-base [29] được lựa chọn làm tiêu chuẩn cơ sở (baseline) nhờ kiến trúc đa ngôn ngữ phổ quát mạnh mẽ và năng lực biểu diễn zero-shot tốt trong các tác vụ truy xuất. Tuy nhiên, thách thức đặt ra là liệu mô hình được huấn luyện trên ngữ liệu đa ngôn ngữ có nắm bắt đủ sâu các thuật ngữ pháp lý đặc thù của Việt Nam hay không.
Ứng viên thứ hai là Legal_hf [13], một biến thể được tinh chỉnh (fine-tuned) chuyên sâu trên tập dữ liệu văn bản quy phạm pháp luật Việt Nam. Giả thuyết nghiên cứu đặt ra là mô hình này sẽ khắc phục được nhược điểm về tri thức chuyên ngành của multilingual-e5-base.
Ứng viên thứ ba là bge-m3 [28], đại diện cho thế hệ mô hình nhúng SOTA (State-of-the-Art) hỗ trợ đa ngôn ngữ với kiến trúc Multi-Vector tiên tiến. Sự xuất hiện của bge-m3 nhằm kiểm chứng giả thuyết: liệu năng lực biểu diễn không gian ngữ nghĩa khổng lồ từ các mô hình hiện đại có thể vượt qua giới hạn của các mô hình chuyên biệt quy mô nhỏ như Legal_hf hay không.
Việc so sánh thực nghiệm giữa ba mô hình này cùng với thuật toán BM25 truyền thống sẽ được trình bày chi tiết trong Chương 4. Kết quả đánh giá bằng các chỉ số định lượng như Recall@k và MRR@10 sẽ là cơ sở khoa học để quyết định mô hình nào được chọn làm "trái tim" (backbone) cho hệ thống, từ đó mở đường cho các bước tinh chỉnh sâu hơn (Domain Adaptation).
3.1.3. Cơ sở dữ liệu vector và cơ chế truy xuất.
Sau giai đoạn mã hóa dữ liệu thành các vector ngữ nghĩa, hệ thống sử dụng thư viện FAISS (Facebook AI Similarity Search) [26] để quản lý việc lưu trữ và thực hiện truy xuất thông tin. Đây là bộ thư viện mã nguồn mở được tối ưu hóa chuyên biệt cho các bài toán tìm kiếm tương đồng trong không gian vector nhiều chiều (high-dimensional space) với tốc độ xử lý vượt trội.
Trong phạm vi nghiên cứu này, FAISS được triển khai theo mô hình cục bộ (local deployment) nhằm đảm bảo quyền kiểm soát tuyệt đối đối với dữ liệu pháp lý nội bộ và tối ưu hóa chi phí vận hành trong môi trường thử nghiệm học thuật. Cơ chế truy xuất dựa trên thuật toán đo độ tương đồng Cosine (Cosine Similarity) để xác định khoảng cách ngữ nghĩa giữa câu hỏi của người dùng và các văn bản đã được đánh chỉ mục. Quy trình xử lý diễn ra theo trình tự khép kín: khi người dùng nhập truy vấn, hệ thống chuyển đổi câu hỏi thành vector thông qua mô hình, sau đó tính toán và trích xuất top-k đoạn văn bản (chunks) có điểm tương đồng cao nhất. Các đoạn văn bản này đóng vai trò là ngữ cảnh đầu vào (context) quan trọng, được chuyển tiếp sang mô hình ngôn ngữ lớn để tổng hợp thành câu trả lời hoàn chỉnh, đảm bảo tính chính xác và căn cứ pháp lý.
3.2. Kiến trúc tổng quan hệ thống.
Hệ thống trợ lý ảo hỗ trợ pháp lý được thiết kế dựa trên kiến trúc phân tầng (multi-tier architecture), tuân thủ nguyên tắc mô-đun hóa nhằm đảm bảo khả năng mở rộng linh hoạt và dễ dàng kiểm thử độc lập trong môi trường nghiên cứu. Mô hình cốt lõi được áp dụng là Sinh văn bản tăng cường truy xuất (Retrieval-Augmented Generation - RAG) [27], bao gồm ba thành phần chức năng chính phối hợp chặt chẽ: tầng tiền xử lý và xây dựng cơ sở tri thức, tầng truy xuất ngữ nghĩa và tầng sinh câu trả lời. Cách tiếp cận này cho phép hệ thống tách biệt dữ liệu tri thức khỏi mô hình ngôn ngữ, giúp dễ dàng cập nhật các văn bản pháp lý mới – điển hình như các nghị định hướng dẫn Luật 72/2025/QH15 [8] – mà không cần huấn luyện lại toàn bộ mô hình (retraining).
Tại tầng đầu tiên, dữ liệu đầu vào bao gồm các văn bản quy phạm pháp luật, nghị định và tài liệu hướng dẫn liên quan đến mô hình chính quyền địa phương hai cấp. Do phần lớn tài liệu tồn tại dưới dạng tệp PDF hoặc văn bản phi cấu trúc, hệ thống tiến hành nhận dạng ký tự quang học (OCR), chuẩn hóa định dạng, loại bỏ nhiễu và chia đoạn văn bản (chunking) theo đơn vị ngữ nghĩa (Điều, Khoản, Điểm). Các đoạn văn bản sau khi làm sạch được đưa qua mô hình nhúng (bi-encoder backbone) để sinh vector biểu diễn ngữ nghĩa. Toàn bộ các vector này được lập chỉ mục và lưu trữ trong cơ sở dữ liệu vector sử dụng thư viện  FAISS [26], tối ưu hóa cho việc truy xuất tốc độ cao.
Tầng thứ hai đảm nhiệm chức năng truy xuất ngữ nghĩa (semantic retrieval), đóng vai trò như bộ lọc thông minh định vị thông tin. Khi người dùng nhập câu hỏi, hệ thống thực hiện chuẩn hóa văn bản truy vấn và chuyển đổi thành vector nhúng trong cùng không gian chiều với cơ sở dữ liệu. Vector truy vấn sau đó được so khớp với tập vector trong FAISS thông qua độ đo tương đồng Cosine (Cosine Similarity) để xác định các đoạn văn bản có mức độ liên quan cao nhất. Ưu điểm vượt trội của cơ chế này so với tìm kiếm từ khóa truyền thống là khả năng hiểu được ý định và ngữ cảnh của câu hỏi, ngay cả khi người dùng sử dụng ngôn ngữ tự nhiên khác biệt với văn phong pháp lý gốc.
Tầng cuối cùng là tầng sinh câu trả lời (generation layer), nơi các đoạn văn bản được truy xuất (top-k kết quả) sẽ được đưa vào mô hình ngôn ngữ lớn để tổng hợp thành phản hồi hoàn chỉnh. Khác với cách hiển thị trích dẫn nguyên văn khô khan, hệ thống tái cấu trúc thông tin theo cách diễn đạt tự nhiên, dễ hiểu nhưng vẫn giữ nguyên nội dung cốt lõi của quy định pháp lý. Việc kết hợp chặt chẽ giữa truy xuất có kiểm soát và sinh ngôn ngữ giúp giảm thiểu đáng kể hiện tượng "ảo giác" (hallucination) thường gặp trong AI, đảm bảo độ tin cậy của kết quả đầu ra.
Hình 3.2. Sơ đồ kiến trúc hệ thống RAG tĩnh
Về mặt vận hành, quy trình xử lý dữ liệu được thiết kế theo luồng tuần tự khép kín: từ thu thập, tiền xử lý, vector hóa dữ liệu đến tiếp nhận truy vấn, truy xuất và sinh phản hồi. Kiến trúc đề xuất này hoàn toàn phù hợp với bối cảnh nghiên cứu học thuật và triển khai thử nghiệm cục bộ (on-premise), đồng thời mở ra khả năng tích hợp linh hoạt với các cổng dịch vụ công trực tuyến hoặc mở rộng sang các lĩnh vực pháp lý chuyên sâu khác trong tương lai.
3.3. Xây dựng và chuẩn hóa cơ sở tri thức.
Cơ sở tri thức (Knowledge Base) cấu thành nền tảng cốt lõi trong kiến trúc hệ thống RAG, mang tính quyết định đối với độ chính xác và mức độ tin cậy của luồng sinh văn bản [27]. Đối với bài toán hỗ trợ tra cứu thủ tục hành chính trong mô hình chính quyền địa phương hai cấp, nguồn dữ liệu tri thức chủ yếu bao gồm các văn bản quy phạm pháp luật, nghị định, thông tư hướng dẫn và các tài liệu hành chính liên đới. Trên thực tế, các tài liệu này tồn tại dưới nhiều định dạng phi cấu trúc khác nhau, phần lớn là các tệp tài liệu quét (scanned PDF), đòi hỏi một quy trình tiền xử lý và chuẩn hóa dữ liệu nghiêm ngặt nhằm tránh hiện tượng suy giảm hiệu suất do nhiễu thông tin [14].
Quá trình kiến tạo cơ sở tri thức được thiết kế thành một chu trình khép kín với các công đoạn trọng tâm sau:
Quá trình trích xuất và tiền xử lý (Data Extraction & Preprocessing): Ở giai đoạn khởi tạo, tập dữ liệu đầu vào được số hóa thông qua các hệ thống nhận dạng ký tự quang học (OCR) [23], [24] nhằm chuyển đổi định dạng ảnh sang văn bản khả đọc bằng máy (machine-readable text). Kế tiếp, tập dữ liệu thô được đưa qua một luồng xử lý tự động (cleaning pipeline) nhằm triệt tiêu các thành phần không mang đặc trưng ngữ nghĩa như: ký tự nhiễu, tiêu đề đầu/cuối trang (header/footer), số trang lặp lại hoặc các sai sót phát sinh từ giới hạn của thuật toán nhận dạng quang học. Việc chuẩn hóa không gian mã hóa Unicode và định dạng cấu trúc câu đóng vai trò tiên quyết nhằm bảo đảm tính đồng nhất tuyệt đối của dữ liệu trước khi thực hiện trích xuất đặc trưng [25].
Phân mảnh văn bản theo ngữ nghĩa (Semantic Chunking): Kế thừa kết quả từ bước tiền xử lý, toàn bộ văn bản được phân rã thành các đơn vị thông tin độc lập. Thay vì cắt gọt cơ học theo số lượng từ, chiến lược phân mảnh được thiết kế theo nguyên lý bảo toàn ngữ nghĩa pháp lý. Cụ thể, mỗi phân đoạn (chunk) được ràng buộc để chứa trọn vẹn một đơn vị kiến thức hoàn chỉnh như một điều luật, một khoản hoặc một quy định cụ thể. Kích thước phân đoạn được kiểm soát chặt chẽ trong ngưỡng 300–500 tokens; đây là tham số thực nghiệm tối ưu nhằm duy trì ngữ cảnh toàn vẹn cho mô hình ngôn ngữ, đồng thời giảm thiểu tỷ lệ nhiễu (noise ratio) trong thuật toán tìm kiếm Top-k. Đặc biệt, hệ thống tích hợp cơ chế gán nhãn siêu dữ liệu (metadata tagging) cho từng phân đoạn — bao gồm tên văn bản, số hiệu điều khoản, ngày ban hành và cơ quan ban hành — nhằm kiến tạo cơ sở đối chiếu cho tác vụ trích dẫn nguồn (source citation) ở chu trình sinh câu trả lời.
Nhúng đặc trưng và Lập chỉ mục không gian vector (Embedding & Indexing): Các phân đoạn văn bản đã chuẩn hóa được biểu diễn dưới dạng vector đa chiều thông qua các mô hình ngôn ngữ như bge-m3 [28] hay Legal_hf[13]. Toàn bộ cơ sở dữ liệu vector sau đó được quản trị và lập chỉ mục (indexing) dựa trên lõi thư viện FAISS (Facebook AI Similarity Search) [26], bảo đảm độ trễ truy vấn thấp và duy trì hiệu năng ổn định khi hệ thống phải xử lý lượng truy xuất quy mô lớn.
Tóm lại, chu trình chuẩn hóa cơ sở tri thức đa tầng này không chỉ tối ưu hóa hiệu suất tìm kiếm mà còn định hình tính minh bạch và khả năng kiểm chứng của toàn bộ kiến trúc RAG. Khi hệ thống tiến hành nội suy câu trả lời, mọi dữ kiện đều có khả năng truy xuất ngược về các văn bản pháp lý gốc, từ đó củng cố độ tin cậy và đáp ứng các tiêu chuẩn khắt khe về tính chính xác trong dịch vụ hành chính công.
Trong định hướng phát triển, kiến trúc cơ sở tri thức được thiết kế theo mô hình mở, sẵn sàng tích hợp các luồng dữ liệu liên thông từ hệ thống quản lý chuyên ngành. Việc ứng dụng các cơ chế thu thập (crawling) và đánh chỉ mục tự động đối với các văn bản quy phạm pháp luật mới ban hành sẽ là giải pháp then chốt giúp hệ thống duy trì tính thời sự, đáp ứng linh hoạt những điều chỉnh liên tục trong khung pháp lý của mô hình chính quyền địa phương hai cấp [8], [9].
3.4. Cơ chế truy xuất ngữ nghĩa và sinh câu trả lời.
Trong kiến trúc RAG, sau khi cơ sở tri thức pháp lý được số hóa và lập chỉ mục không gian vector, quá trình xử lý truy vấn của người dùng được thực hiện thông qua một luồng thuật toán (pipeline) khép kín bao gồm hai khối chức năng cốt lõi: Bộ truy xuất (Retriever) và Bộ sinh câu trả lời (Generator) [27]. Cơ chế này cho phép hệ thống vượt qua các giới hạn về độ dài ngữ cảnh và dữ liệu huấn luyện gốc của Mô hình ngôn ngữ lớn (LLM), đặc biệt hiệu quả đối với các tác vụ đòi hỏi kiến thức chuyên ngành có tính cập nhật cao như tư vấn thủ tục hành chính trong mô hình chính quyền địa phương hai cấp.
3.4.1. Cơ chế Truy xuất ngữ nghĩa (Semantic Retrieval) trong hệ thống pháp lý
Về quy trình tiền xử lý và chuyển hóa không gian Vector (Vector Embedding): Khi người dân nhập các câu hỏi hoặc truy vấn liên quan đến thủ tục pháp lý, hệ thống không tiến hành tìm kiếm từ khóa khô khan mà sẽ kích hoạt Module Xử lý Ngôn ngữ Tự nhiên (NLP). Truy vấn thô sẽ trải qua các bước làm sạch (loại bỏ nhiễu, ký tự đặc biệt), chuẩn hóa từ vựng và phân tách từ (word segmentation). Sau đó, chuỗi văn bản này được chuyển hóa thành các vector đặc trưng (vector embedding) trong không gian đa chiều.
Một nguyên tắc thiết kế bắt buộc trong kiến trúc này là truy vấn đầu vào và cơ sở tri thức pháp lý phải được nhúng bởi cùng một mô hình ngôn ngữ. Việc đồng nhất này đảm bảo các khái niệm có cùng ngữ nghĩa sẽ nằm gần nhau trong không gian vector. Quá trình chọn lọc mô hình đòi hỏi sự cân nhắc kỹ lưỡng giữa các kiến trúc tiền huấn luyện mạnh mẽ (như multilingual-e5-base [29] phổ quát, hoặc Legal_hf [13] cho văn bản luật), và các kiến trúc SOTA tiên tiến như đa ngôn ngữ bge-m3 [28]. Việc thiết lập các mô hình này cần phải đối chiếu bằng các thực nghiệm có hệ thống (sẽ trình bày chi tiết tại Phần 4) nhằm chọn ra nền tảng tốt nhất có khả năng nắm bắt chính xác các thuật ngữ hành chính, từ Hán - Việt và cấu trúc câu phức tạp thường thấy trong văn bản quy phạm pháp luật.
Về thuật toán đối chiếu và tìm kiếm tương đồng (Similarity Search): Sau khi truy vấn được vector hóa, hệ thống sẽ tiến hành đối chiếu nó với hàng triệu vector phân mảnh tài liệu (document chunks) đã được lập chỉ mục sẵn trong Cơ sở dữ liệu Vector (Vector Database). Để giải quyết bài toán tìm kiếm trên không gian dữ liệu khổng lồ này, hệ thống áp dụng các thuật toán tìm kiếm lân cận gần nhất (Approximate Nearest Neighbor - ANN) thông qua thư viện lõi FAISS (Facebook AI Similarity Search) [26].
Mức độ liên quan về mặt ngữ nghĩa giữa vector truy vấn và vector tài liệu được định lượng thông qua các phép đo khoảng cách hình học. Phổ biến nhất là độ tương đồng Cosine (Cosine Similarity), tính toán góc giữa hai vector $A$ và $B$ theo công thức:

$$Cosine (\Theta) = \frac{A \cdot B}{||A|| ||B||} = \frac{\sum_{i=1}^n A_i B_i}{\sqrt{\sum_{i=1}^n A_i^2} \sqrt{\sum_{i=1}^n B_i^2}}$$

Hoặc sử dụng khoảng cách Euclid (L2 distance) để đo độ lệch tuyệt đối trong không gian:

$$L_2 = \sqrt{\sum_{i=1}^n (A_i - B_i)^2}$$

Về trích xuất kết quả và tối ưu hóa tài nguyên (Retrieval Optimization): Dựa trên các chỉ số khoảng cách toán học nêu trên, hệ thống sẽ tự động xếp hạng và trích xuất ra tập hợp Top-k đoạn văn bản (chunks) có mức độ liên quan mật thiết nhất với câu hỏi để làm ngữ cảnh đầu vào cho bộ sinh văn bản (Generator).
Tuy nhiên, với khối lượng dữ liệu pháp luật khổng lồ của mô hình chính quyền hai cấp, việc quét toàn bộ cơ sở dữ liệu cho mỗi truy vấn sẽ gây ra nút thắt cổ chai về mặt hiệu năng. Do đó, để đảm bảo tính khả thi khi triển khai thực tế trên diện rộng, hệ thống được thiết kế tích hợp các kỹ thuật tối ưu hóa truy xuất [11]. Các kỹ thuật này bao gồm lượng tử hóa vector (Vector Quantization), phân cụm dữ liệu (Clustering), và cơ chế lưu trữ đệm (Caching) cho các truy vấn phổ biến, nhằm cân bằng giữa độ chính xác của kết quả, tiết kiệm tài nguyên tính toán và giảm thiểu tối đa độ trễ (latency) của hệ thống. Đồng thời, cấu trúc Reranking nhiều lớp và Truy xuất phân cấp (hybrid) cũng được đề xuất để bù trừ những khiếm khuyết của các nhúng đơn thuần tuyến tính.

3.4.2. Cơ chế Sinh văn bản tăng cường ngữ cảnh
Tiếp nối giai đoạn truy xuất ngữ nghĩa, tập hợp các đoạn văn bản pháp luật (Top-k chunks) mang tính liên quan cao nhất sẽ được chuyển tiếp sang module Sinh văn bản (Generator). Tại đây, Mô hình Ngôn ngữ Lớn (Large Language Model - LLM) không hoạt động như một cỗ máy trả lời tự do dựa trên tham số nội tại, mà đóng vai trò là một bộ tổng hợp và suy luận có kiểm soát. Quá trình này được thực hiện qua các bước kỹ thuật chặt chẽ sau:
Thứ nhất, kỹ thuật lồng ghép ngữ cảnh và xây dựng lời nhắc (Prompt Engineering): Hệ thống không đẩy trực tiếp câu hỏi của người dân vào LLM. Thay vào đó, một bộ điều phối (orchestrator) sẽ tự động cấu trúc lại dữ liệu đầu vào thông qua các mẫu lời nhắc (prompt templates) được thiết kế đặc thù cho lĩnh vực pháp lý. Lời nhắc này là sự đóng gói hoàn chỉnh bao gồm: (1) Chỉ thị hệ thống (System Prompt) ép buộc LLM chỉ được phép trả lời dựa trên ngữ cảnh cung cấp; (2) Tập hợp các văn bản luật Top-k (C={c1​,c2​,...,ck​}) vừa được truy xuất; và (3) Câu hỏi nguyên gốc của người dùng (q).
Về mặt xác suất, mục tiêu của mô hình sinh văn bản là tìm ra chuỗi từ vựng đầu ra (câu trả lời y) sao cho tối đa hóa hàm xác suất có điều kiện dựa trên cả câu hỏi và ngữ cảnh được cung cấp:

Thứ hai, quá trình tổng hợp và giới hạn ảo giác (Hallucination Mitigation): Khi tiếp nhận gói thông tin trên, LLM sẽ sử dụng cơ chế chú ý (Attention Mechanism) để phân tích chéo giữa ý định trong truy vấn và các điều khoản luật trong ngữ cảnh. Nhờ có "chiếc mỏ neo" là dữ liệu thực tế (C), mô hình bị triệt tiêu không gian sáng tạo tự do, qua đó khắc phục triệt để điểm yếu chí mạng của các chatbot truyền thống là hiện tượng "ảo giác thông tin" (hallucination). Đối với các TTHC phức tạp trong mô hình chính quyền hai cấp, sự kiểm soát này đảm bảo hệ thống không tự bịa ra các cơ quan không có thẩm quyền hoặc các mức lệ phí không tồn tại trong luật.
Thứ ba, định dạng đầu ra và trích dẫn minh bạch (Citation Formatting): Khác với các đoạn chat thông thường, đầu ra của module Sinh văn bản trong hệ thống pháp lý bị ràng buộc bởi các quy chuẩn về hình thức. Câu trả lời cuối cùng được thiết kế để xuất ra theo hai phần rõ rệt:
Phần tư vấn: Diễn giải điều luật bằng ngôn ngữ tự nhiên, mạch lạc, dễ hiểu đối với công dân không có chuyên môn luật học.
Phần căn cứ pháp lý: Trích dẫn chính xác và minh bạch nguồn gốc thông tin (ví dụ: "Căn cứ theo Điểm a, Khoản 2, Điều X, Nghị định Y...").
Nếu tập ngữ cảnh C không chứa đủ thông tin để giải quyết câu hỏi q, hệ thống được lập trình để chủ động từ chối trả lời hoặc yêu cầu người dân cung cấp thêm thông tin, tuyệt đối không đưa ra các phỏng đoán thiếu căn cứ. Điều này giúp bảo vệ tính toàn vẹn và độ tin cậy của toàn bộ hệ thống tư vấn pháp luật tự động.
3.5. Triển khai và hệ thống hóa thực nghiệm.
Quá trình cấu hình kiểm thử môi trường và triển khai đánh giá hiệu năng đo lường đối với các thành phần của hệ thống RAG sẽ được trình bày hệ thống hóa thông qua các kịch bản thực nghiệm định lượng ở Chương 4.

Chương 4. Thực nghiệm và đánh giá
4.1. Thiết lập tập dữ liệu thực nghiệm.
Bộ dữ liệu kiểm định được xây dựng nhằm đánh giá khách quan năng lực truy xuất thông tin của hệ thống hỏi đáp pháp lý về chính quyền địa phương hai cấp. Tập dữ liệu bao gồm các cặp truy vấn và đoạn văn bản đáp án chuẩn (ground truth), được trích xuất và tổng hợp thủ công từ các điều khoản của Luật Tổ chức chính quyền địa phương số 72/2025/QH15, các nghị định, thông tư và văn bản hướng dẫn liên quan đến mô hình chính quyền địa phương hai cấp [8], [9].

Mỗi truy vấn được biểu diễn dưới dạng câu hỏi bằng ngôn ngữ tự nhiên, mô phỏng cách người dân đặt câu hỏi trong thực tế. Đáp án chuẩn tương ứng là một hoặc nhiều đoạn văn bản pháp luật (passage) giải quyết trực tiếp truy vấn đó. Toàn bộ corpus được phân chia thành tập huấn luyện và tập đánh giá cố định để đảm bảo tính công bằng khi so sánh chéo giữa các cấu hình mô hình.


Tham số	Giá trị
Tổng số passages (corpus)	1.840
Số truy vấn đánh giá (eval)	570
Số truy vấn huấn luyện (train)	2.788


Bảng 4.1. Cấu trúc bộ dữ liệu kiểm thử

Để minh họa cụ thể, một mẫu trong tập đánh giá có dạng như sau:

Query (Câu hỏi)	Passage (Đoạn văn đáp án - Trích lược)	Văn bản (Meta)	Điều/Khoản
Kinh phí thực hiện nhiệm vụ chuyển giao do ai đảm bảo?	Khoản 9 Điều 2 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp...	NGHỊ ĐỊNH phân định thẩm quyền...	Điều 2 - Khoản 9
Thẩm quyền của chính quyền địa phương hai cấp trong lĩnh vực quản lý nhà nước quy định ở đâu?	Khoản 9 Điều 2 NGHỊ ĐỊNH Quy định về phân định thẩm quyền...	NGHỊ ĐỊNH phân định thẩm quyền...	Điều 2 - Khoản 9


4.2. Tiêu chí và phương pháp đánh giá.
Chất lượng hệ thống được đánh giá tập trung tại tầng truy xuất ngữ nghĩa (Semantic Retrieval). Nghiên cứu sử dụng các độ đo tiêu chuẩn trong lĩnh vực Truy xuất thông tin (Information Retrieval) bao gồm Recall@k và MRR@10.

4.2.1. Độ đo Recall@k
Recall@k đo lường tỷ lệ các truy vấn mà trong top-k kết quả trả về có chứa ít nhất một đáp án đúng. Công thức tính được định nghĩa như sau:

Chỉ số này phản ánh trực tiếp khả năng bao phủ tài liệu liên quan của hệ thống. Trong nghiên cứu này, các giá trị k được khảo sát bao gồm 1, 3 và 5.

4.2.2. Độ đo MRR@10
MRR@10 đánh giá chất lượng xếp hạng dựa trên trung bình cộng nghịch đảo thứ hạng đáp án đúng đầu tiên:

Trong đó N là tổng số truy vấn và ranki là vị trí của đáp án đúng đối với truy vấn thứ i (giới hạn top 10). Giá trị MRR càng tiệm cận 1 thể hiện hệ thống đưa đáp án chính xác lên vị trí cao hơn. Hai chỉ số này bổ sung cho nhau: Recall@1 phản ánh khả năng truy xuất chính xác ở vị trí đầu tiên, còn MRR@10 đánh giá chất lượng xếp hạng trung bình toàn bộ tập đánh giá.

4.3. Kết quả thực nghiệm
Nghiên cứu tiến hành đánh giá và so sánh hiệu năng hệ thống theo từng giai đoạn nâng cấp cấu hình, từ các mô hình nền (baseline) đến các cấu hình đã được tinh chỉnh (fine-tuned) và kết hợp nâng cao. Toàn bộ thực nghiệm sử dụng cùng một bộ dữ liệu kiểm thử, phương pháp đánh giá cố định và được chạy trong cùng môi trường phần cứng nhằm đảm bảo tính so sánh công bằng.



4.3.1. Giai đoạn 1: Đánh giá các mô hình cơ sở (Baseline) từ V1 đến V2.3
Mục đích thực nghiệm:
Thiết lập các mức tham chiếu (baseline) cho hệ thống trước khi áp dụng bất kỳ kỹ thuật tinh chỉnh nào. Thực nghiệm so sánh giữa phương pháp đối sánh từ khóa truyền thống (BM25) và các mô hình biểu diễn không gian ngữ nghĩa Dense Retrieval nguyên bản (off-shelf) bao gồm: multilingual-e5-base (đa ngôn ngữ phổ quát), Legal_hf (chuyên biệt pháp lý quy mô nhỏ), và bge-m3 (SOTA đa ngôn ngữ quy mô lớn).

Tiêu chí	BM25 (V1)	multilingual-e5-base (V2.1)	Legal_hf (V2.2)	bge-m3 (V2.3)
Recall@1	0.5140	0.4614	0.3175	0.4719
Recall@3	0.7070	0.6298	0.4737	0.6283
Recall@5	0.7807	0.7035	0.5351	0.7228
Recall@100	—	0.9070	0.8298	0.9246
MRR@10	0.6190	0.5543	0.4020	0.5685

Bảng 4.2. So sánh hiệu năng các phương pháp truy xuất cơ sở (Baseline)

Phân tích và Thảo luận:
*   Ưu thế của BM25 (V1): Kết quả chỉ ra BM25 đạt tỷ lệ Recall@1 cao nhất ở nhóm baseline (0.5140) và MRR@10 cao nhất (0.6190). Điều này bắt nguồn từ đặc thù của văn bản pháp quy Việt Nam, nơi các thuật ngữ định danh (Exact Match) như "Nghị quyết 268", "Thẩm quyền" đóng vai trò cốt lõi. Phương pháp khớp từ vựng (Sparse Retrieval) vẫn chứng minh độ ổn định xuất sắc khi xử lý các truy vấn có tính chính xác từ khóa cao.
*   Sự hụt hơi của mô hình chuyên biệt Legal_hf (V2.2): Trái với kỳ vọng về một mô hình tinh chỉnh riêng cho văn bản luật, Legal_hf thể hiện hiệu năng sa sút nghiêm trọng nhất (Recall@1 chỉ đạt 0.3175, Recall@100 là 0.8298). Nguyên nhân có thể do corpus luật của bộ dữ liệu huấn luyện Legal_hf quá cũ hoặc sự giới hạn về quy mô tham số khiến mô hình không đủ sức nắm bắt ngữ nghĩa phức tạp của chính quyền đô thị hiện đại.
*   Hiệu suất Dense Retrieval Đa ngôn ngữ (V2.1 & V2.3): Cả hai đại diện đa ngôn ngữ là `multilingual-e5-base` và `bge-m3` đều cho thấy sức mạnh không gian vector ấn tượng với Recall@100 vượt mốc 90%. Trong đó, `bge-m3` nhỉnh hơn (Recall@1 = 0.4719, Recall@100 = 0.9246) so với đối thủ `e5-base`. Điều này chứng minh kiến trúc Multi-Vector và tập dữ liệu tiền huấn luyện đa ngôn ngữ đồ sộ của `bge-m3` có khả năng tổng quát hóa (generalization) rất mạnh mẽ trên miền dữ liệu pháp lý mà không cần huấn luyện trước chuyên sâu (zero-shot).

Kết luận Rút ra: Ở trạng thái chưa tinh chỉnh, thuật toán BM25 vẫn là phương pháp chiếm ưu thế nhất trong việc chốt chính xác kết quả đầu tiên. Tuy nhiên, với tiềm năng bao quát ngữ nghĩa mạnh mẽ (Recall@100 cao nhất), `bge-m3` và `multilingual-e5-base` cung cấp nền tảng Dense đáng tin cậy. Dựa trên chỉ số tổng thể vượt trội, `bge-m3` chính thức được lựa chọn làm backbone bền vững cho chu trình kiến tạo hệ thống RAG tiếp theo nhằm phá vỡ rào cản "khớp đúng chuỗi" của BM25.

4.3.2. Giai đoạn 2: Bổ sung Cơ chế Tái xếp hạng (Cross-Encoder) với V3
Mục đích thực nghiệm:
Xác định tác động của kiến trúc Cross-Encoder (CE) khi được xếp chồng (pipeline) lên kết quả trả về của Bi-encoder (Top-100 từ V2.3). CE có khả năng tính toán sự chú ý chéo (Cross-Attention) trực tiếp giữa truy vấn và tài liệu, hứa hẹn tối ưu hóa thứ hạng trả về (MRR).

Tiêu chí	bge-m3 off-shelf (V2.3)	+ ms-marco CE (V3.1)	+ bge-reranker CE (V3.2)
Recall@1	0.4719	0.3600	0.5877
Recall@3	0.6283	0.5547	0.7283
Recall@5	0.7228	0.6107	0.8053
MRR@10	0.5685	0.4540	0.6794

Bảng 4.3. Tác động của Cross-Encoder Reranking trên nền bge-m3

Phân tích và Thảo luận:
*   Hiện tượng rào cản ngôn ngữ (Language Mismatch): Mô hình `ms-marco-MiniLM` (V3.1) — vốn kiến trúc từ dữ liệu MS-MARCO tiếng Anh — bộc lộ sự thiếu tương thích nghiêm trọng khi áp dụng zero-shot lên miền dữ liệu tiếng Việt. Chỉ số Recall@1 sụt giảm mạnh từ 0.4719 xuống 0.3600. Sự thiếu hụt vốn từ vựng hệ pháp lý khiến thuật toán Attention của Cross-Encoder bị nhiễu loạn trong quá trình phân loại ranh giới âm/dương tính của văn bản.
*   Sức mạnh cộng hưởng của CE Đa ngôn ngữ: Khi thay thế bằng mô hình được thiết kế triệt để cho tác vụ tái xếp hạng `bge-reranker-v2-m3` (V3.2), Recall@1 lập tức tăng bức phá lên mốc 0.5877 (+11.58 điểm % so với V2.3). Cơ chế Self-Attention toàn cục ở tầng trên đã giải quyết xuất sắc những điểm mù ngữ nghĩa mà phép đo Cosine Similarity đơn tuyến ở tầng Bi-encoder phía dưới không thể chạm tới.

Kết luận Rút ra: Trong trạng thái kiến trúc chưa can thiệp tinh chỉnh (zero-shot), thuật toán Tái xếp hạng (Cross-Encoder Reranking) đóng vai trò như một màng lọc tối quan trọng giúp "vớt" các văn bản chân lý bị chìm lấp lên vị trí hàng đầu (kéo điểm MRR@10 tăng mạnh lên 0.6794). Tuy nhiên, ranh giới sinh tồn của CE phụ thuộc tuyệt đối vào sự hòa hợp ngôn ngữ lõi (ngữ liệu huấn luyện tiếng Việt). Hạn chế đánh đổi duy nhất nằm ở hao tốn tài nguyên tính toán (chi phí Inference) phình to tuyến tính theo số lượng văn bản nạp vào.

4.3.3. Giai đoạn 3: Tinh chỉnh miền (Domain Adaptation) cho Bi-encoder - V4
Mục đích thực nghiệm:
Kiểm chứng giả thuyết rằng: Việc tinh chỉnh trực tiếp mô hình Bi-encoder (Fine-tuning) bằng hàm mất mát MultipleNegativesRankingLoss trên đặc thù ngôn ngữ hành chính luật Việt Nam sẽ tạo ra giá trị lõi bền vững hơn việc chỉ dùng kỹ thuật ghép nối pipeline off-shelf.

Tiêu chí	bge-m3 + CE off-shelf (V3.2)	FT bge-m3 bi-only (V4)
Recall@1	0.5877	0.6070
Recall@3	0.7283	0.7947
Recall@5	0.8053	0.8333
Recall@100	—	0.9737
MRR@10	0.6794	0.7020

Bảng 4.4. Hiệu năng của hệ thống bge-m3 sau quá trình Domain Fine-Tuning

Phân tích và Thảo luận:
*   Sức bật từ học chuyển giao (Transfer Learning): Hệ thống thuần Bi-encoder sau khi Fine-tune (V4) đạt R@1 = 0.6070, đánh bại ngoạn mục cấu trúc hai tầng phức tạp V3.2. Việc buộc không gian vector tái cấu trúc theo hàm suy hao Contrastive Loss giúp mô hình thấu hiểu trực tiếp khoảng cách giữa câu từ sinh hoạt của người dân và thuật ngữ pháp lý.
*   Trần bao quát tri thức (Upper Bound Coverage): Chỉ số Recall@100 đạt mức 0.9737, khẳng định cơ sở dữ liệu vector đã bắt được hơn 97.4% lượng đáp án chuẩn trong 100 kết quả đầu ra. 

Kết luận Rút ra: Tinh chỉnh miền trực tiếp (Domain Adaptation) trên Bi-encoder là bước can thiệp hạt nhân mang lại hiệu suất lợi thế kép (Dual - Advantage): (1) Nâng cao hiệu năng truy xuất mạnh mẽ nhất (R@1 +28.6% so với zero-shot), (2) Tốc độ phản hồi cực nhanh nhờ kiến trúc tính toán offline trên FAISS. Đây là nền móng lõi (Core Engine) tĩnh để triển khai các thuật toán cải tiến cấp cao hơn ở giai đoạn sau. Ưu tiên giải quyết triệt để sự đứt gãy từ vựng ở tầng dưới cùng mang lại ROI (Tỷ suất hoàn vốn đầu tư tài nguyên) xuất sắc nhất.

4.3.4. Giai đoạn 4: Tinh chỉnh Cross-Encoder Khai thác Mẫu Âm tính (Hard Negative Mining) - V5 và V6
Mục đích thực nghiệm:
Nâng cao năng lực phân loại sắc thái của Cross-Encoder (đã được tinh chỉnh). Trong lĩnh vực luật, nhiều đoạn văn bản rất giống nhau (điều lệ, chức năng, nhiệm vụ trùng lặp cho nhiều cấp). Thực nghiệm đánh giá ảnh hưởng của độ khó Mẫu Âm tính (Hard Negatives) trong quá trình huấn luyện: V5 lấy mẫu âm thuộc Top-20, V6 lấy mẫu âm khắc nghiệt hơn từ Top-5.

Tiêu chí	FT bi only (V4)	FT bi + FT CE top-20 (V5)	FT bi + FT CE top-5 (V6)
Recall@1	0.6070	0.6123	0.6368
Recall@3	0.7947	0.8053	0.8158
Recall@5	0.8333	0.8509	0.8544
MRR@10	0.7020	0.7119	0.7282

Bảng 4.5. So sánh chiến lược Hard Negative Mining cho việc fine-tuning Cross-Encoder

Phân tích và Thảo luận:
*   Hạn chế của Hard Negatives dải rộng (V5): Phương pháp bốc mẫu ngẫu nhiên từ dải phân bổ xấp xỉ Top-20 chỉ kéo Recall@1 nhích nhẹ lên mức 0.6123 (+0.5% so với V4). Do các văn bản mồi nhử ở xa vị trí chân lý (từ hạng 10 đến 20) thường mang đặc trưng ngữ nghĩa khác biệt hẳn về chủ đề, hàm đánh giá (Loss Function) không học được cách phân biệt các ranh giới vi tế của pháp luật.
*   Độ phân giải ngữ nghĩa cấp vi mô (Micro-semantics) của V6: Việc siết chặt dải khai thác mẫu âm tính xuống Top-5 buộc mô hình phải học thao tác "soi chi tiết" từng từ vựng định danh đặc thù (ví dụ: phân định rạch ròi Thẩm quyền của Chủ tịch Tỉnh so với Quyền hạn của Chủ tịch Phường). Nhờ chiến thuật ép xung này, Recall@1 chính thức phá vỡ trần và xác lập đỉnh 0.6368, cùng với chỉ số MRR@10 vươn lên mốc đầu bảng 0.7282.

Kết luận Rút ra: Khi bản thân Bi-encoder đã mạnh, Cross-Encoder không còn là bộ vá khiếm khuyết đơn thuần mà lột xác thành "máy mài góc" (fine-tuner layer) triệt tiêu các điểm mù tuyến tính. Chất lượng đường phân chia quyết định (Decision Boundary) của mô hình bị ràng buộc mật thiết bởi độ sát nghĩa cực đoan trong khâu rà soát Negative Mining. Cấu trúc V6 chính là trạng thái cân bằng hoàn hảo nhất để tối đa hóa hiệu năng truy xuất hành chính.

4.3.5. Giai đoạn 5: Phân tích Lợi tức Giảm dần (Diminishing Returns) và Cải tiến mở rộng (Ablation V7)
Mục đích thực nghiệm:
Kiểm định giả thuyết về "Lợi tức giảm dần" trong Truy xuất Thông tin. Đánh giá xem trên một không gian vector (V6) đã được tinh chỉnh đạt tỷ lệ bao phủ R@100 = 0.97, liệu các mô hình truy xuất tăng cường như Kết hợp RRF (Hybrid) hay tạo sinh truy vấn giả lập (HyDE - Qwen3.5 LLM) có còn không gian để tỏa sáng?

Tiêu chí	V6 (best)	V7.1 Hybrid RRF	V7.2 HyDE	V7.3 Combo
Recall@1	0.6368	0.6368	0.6404	0.6368
Recall@3	0.8158	0.8123	0.8158	0.8123
Recall@5	0.8544	0.8474	0.8509	0.8474
MRR@10	0.7282	0.7258	0.7294	0.7259

Bảng 4.6. Ablation Study kỹ thuật truy xuất nâng cao trên nền hệ thống V6

Phân tích và Thảo luận:
*   Trạng thái bão hòa của Hợp nhất hạng (V7.1 Hybrid): Phương pháp Reciprocal Rank Fusion kết hợp BM25 không mang lại bất cứ cải tiến nào về giá trị Recall@1. Lý do cốt lõi: đối chiếu với một kho dữ liệu (Corpus) quy mô nhỏ, mô hình Dense FT (V4) đã thâu tóm xuất sắc năng lực tra khớp của BM25. Hiện tượng bù trừ khuyết điểm chéo (Orthogonal Signal) không còn dư địa để diễn ra.
*   Nút thắt về Chi phí Gen-time (V7.2 HyDE): Cơ chế HyDE đạt mức Recall@1 tuyệt đối cao nhất 0.6404 nhờ tận dụng LLM nội suy giải nghĩa truy vấn (Query Expansion). Bù lại, sự phức tạp vì phải kích hoạt LLM sinh văn bản làm tăng vọt hệ số trễ nội tại của hệ thống, và thực tế làm sụt giảm R@5 do rủi ro từ lỗi Hallucination của LLM gây xáo trộn từ vựng đích.
*   Hiện tượng Diminishing Returns (V7.3): Việc dồn ép toàn bộ kỹ thuật (Dense + Sparse + HyDE) giao thoa bằng RRF ở V7.3 đã làm sụp đổ các lợi thế vi mô, khiến chi phí tài nguyên phình to theo cấp số nhân trong khi hiệu năng lại lùi về điểm mốc 0.6368.

Kết luận Rút ra: Nghiên cứu thực nghiệm chứng minh xác đáng giả thuyết về Lợi tức Giảm dần (Diminishing Returns). Khi cấu trúc Base Representation đã được thực hiện tinh chỉnh dải ngành đích (Domain-Adapted) đạt mức bão hòa, các cơ chế bọc ngoài ngoại biên (Ensemble) sẽ chỉ cung cấp phần lợi tức tiệm cận mức 0 (Marginal Gain). Hệ thống V6 (Bi-encoder FT + CE Top-5) được ấn định là kiến trúc hệ thống chính thức vì nó nắm giữ "điểm tối ưu trên đường Pareto" để dung hòa bài toán hiệu năng và hao phí phần cứng.

4.4. Phân tích, nhận xét và hạn chế của hệ thống
Từ kết quả thực nghiệm định lượng toàn bộ nêu trên, nghiên cứu rút ra một số kết luận chuyên môn sau:

Về mô hình nhúng: Fine-tuning bi-encoder bge-m3 trực tiếp trên dữ liệu pháp lý chính quyền hai cấp là can thiệp kiến trúc mang lại mức tăng lớn nhất (từ Recall@1 = 0.472 của zero-shot lên 0.607 sau tinh chỉnh, tương đương 28.6%). Kết quả này vượt trội so với các hướng tiếp cận dùng mô hình nhúng mặc định hoặc mô hình thay thế (như sơ bộ của e5 hay Legal_hf), khẳng định tính chất tiên quyết đối với bài toán domain-specific: tinh chỉnh trực tiếp trên bộ dữ liệu quy phạm nội tại sẽ mang lại sức bật mạnh nhất.

Về kiến trúc truy xuất: Cross-encoder Reranking đóng vai trò cứu cánh dự phòng quan trọng khi chất lượng embedding gốc chưa tối ưu (chuẩn hóa ở V3.2 làm tăng +11.6% R@1). Sau khi bi-encoder bge-m3 đã được fine-tune xuất sắc, tầng CE (thừa kế tập tham số đối sánh sâu của PhoBERT) vẫn tiếp tục thu hoạch thêm +3.0% Recall@1 (V6). Công trình cho thấy phối hợp đồng nhất giữa năng lực ngữ nghĩa không gian của M3 và sự chú ý bắt chéo sâu sắc của PhoBERT mang lại sức đề kháng cao chống lại thuật ngữ gây nhầm lẫn.

Về kỹ thuật nâng cao: Đối diện thực tế corpus thuộc diện nhỏ gọn và bi-encoder đã được tinh chỉnh đẩy tới giới hạn vận hành (Recall@100 = 0.974), các kỹ thuật Hybrid Retrieval và HyDE chỉ cung ứng marginal improvement (lợi thế chênh lệch nhỏ) hoặc phản tác dụng. Đây thực chất là một negative finding có giá trị khoa học thiết thực, phản ánh chân thực trần bão hòa của các kỹ thuật tìm kiếm khi áp dụng trong môi trường bị khống chế kích thước lưu trữ.

Bên cạnh những kết quả định lượng khởi sắc, cấu hình hệ thống thử nghiệm vẫn tồn đọng một số vướng mắc đặc thù. Corpus kiểm định quy mô nhỏ (1.840 passages) tạo thành mặt hạn chế giới hạn khả năng bao quát khái quát hóa tri thức diện rộng sang các bộ luật hành chính pháp lý khác. Chất lượng truy xuất nội tại vẫn phải gánh chịu sai số dây chuyền phái sinh từ khâu nhận dạng quang học (OCR) xử lý tài liệu PDF quá mờ [14]. Đặc biệt, khả năng giải quyết các câu hỏi yêu cầu kỹ năng suy luận xuyên suốt đa nhánh (multi-hop reasoning) — khi chuỗi đáp án nằm rải rác đứt đoạn ở nhiều điều khoản — vẫn chưa được tháo gỡ triệt để. Cuối cùng, việc triển khai vận hành song song một Bi-encoder và Cross-encoder dung lượng lớn làm phình to yêu cầu phần cứng làm tăng độ phi mã thời gian kiến thiết truy vấn (latency cost). Những tồn đọng này tạo cơ sở luận điểm vững chắc để định hướng cho các luận án mở rộng tiếp theo, tập trung thu thập bổ cứu dữ liệu lớn và áp dụng công nghệ lượng tử siêu việt cho việc thu gọn bộ nhớ mô hình (model quantization).


PHẦN KẾT LUẬN
Nghiên cứu đã đề xuất và triển khai thành công hệ thống hỗ trợ tra cứu thủ tục hành chính dựa trên kiến trúc Sinh văn bản tăng cường truy xuất (RAG), chuyên biệt hóa cho miền tri thức về mô hình chính quyền địa phương hai cấp theo Luật số 72/2025/QH15. Nghiên cứu đã giải quyết hiệu quả bài toán số hóa, phân mảnh ngữ nghĩa (semantic chunking) theo chuẩn cấu trúc pháp luật Việt Nam và xây dựng một bộ dữ liệu kiểm định (benchmark dataset) gồm 1.840 passages và 570 truy vấn đánh giá, phục vụ cho tác vụ hỏi đáp hành chính công.
Kết quả thực nghiệm định lượng toàn diện (V1 đến V7) đã làm sáng tỏ vai trò của từng thành phần trong kiến trúc RAG. Thứ nhất, BM25 vẫn là baseline cạnh tranh (Recall@1 = 0.514) trong ngữ cảnh pháp luật tiếng Việt. Thứ hai, bge-m3 được công nhận là backbone tốt nhất (Recall@1 = 0.472) trong số các mô hình cấu hình gốc, ổn định hơn so với cấu trúc của multilingual-e5-base hay Legal_hf. Thứ ba, domain fine-tuning bi-encoder trực tiếp trên dữ liệu đích là can thiệp mang lại mức tăng đột phá nhất (từ 0.472 lên 0.607, tăng 28.6%), vượt cả BM25 lần đầu tiên. Thứ tư, fine-tuning Cross-encoder (sử dụng PhoBERT) với chiến lược hard negative mining từ top-5 (V6) bổ sung thêm +3.0% Recall@1, đạt Recall@1 = 0.637 và MRR@10 = 0.728 — là hệ thống chạy tối ưu hiệu năng tốt nhất trong nghiên cứu. Thứ năm, với bi-encoder đã fine-tune bao phủ 97.4% câu trả lời trong top-100, các kỹ thuật Hybrid Retrieval và HyDE chỉ cung cấp biên lợi nhuận thấp, minh chứng cho sự bão hòa tối ưu.
Trong các nghiên cứu tiếp theo, hệ thống sẽ được mở rộng năng lực xử lý suy luận đa bước (multi-hop reasoning) đối với các câu hỏi liên quan đến nhiều điều khoản khác nhau, cùng với việc mở rộng corpus và tích hợp kỹ thuật lượng tử hóa mô hình (model quantization) nhằm tối ưu hóa hiệu năng triển khai tại các cổng dịch vụ công trực tuyến.









TÀI LIỆU THAM KHẢO

(Liệt kê tài liệu theo chuẩn APA 6th Edition hoặc IEEE)
[1] Diệp Văn Sơn (2020). Chính quyền đô thị ở Việt Nam – từ góc độ thực tiễn quản lý. Tạp chí Quản lý nhà nước. Truy cập từ: https://www.quanlynhanuoc.vn/2020/08/04/chinh-quyen-do-thi-o-viet-nam-tu-goc-do-thuc-tien-quan-ly/
[2] Đặng Đình Thái (2024). Hoàn thiện chính sách xây dựng chính quyền đô thị ở Việt Nam hiện nay. Tạp chí Quản lý nhà nước. Truy cập từ: https://www.quanlynhanuoc.vn/2024/07/23/hoan-thien-chinh-sach-xay-dung-chinh-quyen-do-thi-o-viet-nam-hien-nay/ 
[3] Phạm Thị Ngọc Huệ, Tôn Tường Oanh (2024). Khảo sát sự hài lòng của người dân về dịch vụ công trực tuyến trên địa bàn tỉnh Bình Phước. Tạp chí Khoa học Đại học Bạc Liêu. Truy cập từ: https://vjol.info.vn/index.php/tckhdhBacLieu/article/download/108850/91390/ 
[4] Nguyễn Hoàng Sơn (2020). Phân tích sự hài lòng của người dân đối với dịch vụ hành chính công tại Ủy ban nhân dân huyện Tuy An, tỉnh Phú Yên. Tạp chí Công Thương. Truy cập từ: https://tapchicongthuong.vn/phan-tich-su-hai-long-cua-nguoi-dan-doi-voi-dich-vu-hanh-chinh-cong-tai-uy-ban-nhan-dan-huyen-tuy-an--tinh-phu-yen-73645.htm 
[5] Cổng thông tin điện tử UBND Xã Cẩm Thạch, Thanh Hóa (2024). Ứng dụng trí tuệ nhân tạo nâng cao hiệu quả cung cấp dịch vụ công. Truy cập từ: https://camthach.thanhhoa.gov.vn/chuyen-doi-so/ung-dung-tri-tue-nhan-tao-nang-cao-hieu-qua-cung-cap-dich-vu-cong-563842 
[6] Cổng TTĐT Chuyển đổi số tỉnh Lào Cai (2024). Dân vùng khó khăn dễ dàng thực hiện thủ tục hành chính với Dịch vụ công AI. (Nói về dự án DVC AI của UNDP và Viện IPS). Truy cập từ: https://chuyendoiso.laocai.gov.vn/tin-trong-nuoc/dan-vung-kho-khan-de-dang-thuc-hien-thu-tuc-hanh-chinh-voi-dich-vu-cong-ai-1306172 
[7] Cổng thông tin điện tử Bộ Xây dựng (2025). Bộ Xây dựng triển khai Tổng đài thông minh ứng dựng AI hỗ trợ thủ tục hành chính. Truy cập từ: https://moc.gov.vn/vn/tin-tuc/1305/85741/bo-xay-dung-trien-khai-tong-dai-thong-minh-ung-dung-ai-ho-tro-thu-tuc-hanh-chinh.aspx
[8] Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam, "Luật Tổ chức chính quyền địa phương," Luật số 72/2025/QH15, ban hành ngày 16/06/2025.
[9] Chính phủ nước Cộng hòa xã hội chủ nghĩa Việt Nam, "Nghị quyết về tình hình triển khai thực hiện và vận hành mô hình chính quyền địa phương 02 cấp," Nghị quyết số 268/NQ-CP, ban hành ngày 31/08/2025.
[10] Chính phủ nước Cộng hòa xã hội chủ nghĩa Việt Nam, "Nghị định quy định chi tiết và biện pháp thi hành Nghị quyết số 97/2019/QH14 ngày 27/11/2019 của Quốc hội về thí điểm tổ chức mô hình chính quyền đô thị tại thành phố Hà Nội," Nghị định số 32/2021/NĐ-CP, ban hành ngày 29/03/2021.
[11] Z. Wang, H. Yuan, W. Dong, G. Cong, and F. Li, "CORAG: A Cost-Constrained Retrieval Optimization System for Retrieval-Augmented Generation," Proc. VLDB Endow., vol. 14, no. 1, Nov. 2024.
[12] D. Q. Nguyen and A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," in Findings of the Association for Computational Linguistics: EMNLP 2020, Nov. 2020, pp. 1037-1042.
[13] Quockhanh05, "Vietnamese Legal Embedding Model," Hugging Face, 2024. [Online]. Available: https://huggingface.co/Quockhanh05/Vietnam_legal_embeddings.
[14] J. Zhang et al., "OCR Hinders RAG: Evaluating the Cascading Impact of OCR on Retrieval-Augmented Generation," arXiv preprint arXiv:2412.02592, Aug. 2025.
[15] Q. Cuong, "ChatBot," GitHub repository, 2024. [Online]. Available: https://github.com/QuoocsCuongwf/ChatBot.
[16] D. V. Sơn, "Chính quyền đô thị ở Việt Nam – từ góc độ thực tiễn quản lý," Tạp chí Quản lý nhà nước, Aug. 2020. [Online]. Available: https://www.quanlynhanuoc.vn/2020/08/04/chinh-quyen-do-thi-o-viet-nam-tu-goc-do-thuc-tien-quan-ly/.
[17] Đ. Đ. Thái, "Hoàn thiện chính sách xây dựng chính quyền đô thị ở Việt Nam hiện nay," Tạp chí Quản lý nhà nước, Jul. 2024. [Online]. Available: https://www.quanlynhanuoc.vn/2024/07/23/hoan-thien-chinh-sach-xay-dung-chinh-quyen-do-thi-o-viet-nam-hien-nay/.
[18] P. T. N. Huệ and T. T. Oanh, "Khảo sát sự hài lòng của người dân về dịch vụ công trực tuyến trên địa bàn tỉnh Bình Phước," Tạp chí Khoa học Đại học Bạc Liêu, 2024. [Online]. Available: https://vjol.info.vn/index.php/tckhdhBacLieu/article/download/108850/91390/.
[19] N. H. Sơn, "Phân tích sự hài lòng của người dân đối với dịch vụ hành chính công tại Ủy ban nhân dân huyện Tuy An, tỉnh Phú Yên," Tạp chí Công Thương, 2020. [Online]. Available: https://tapchicongthuong.vn/phan-tich-su-hai-long-cua-nguoi-dan-doi-voi-dich-vu-hanh-chinh-cong-tai-uy-ban-nhan-dan-huyen-tuy-an--tinh-phu-yen-73645.htm.
[20] Cổng thông tin điện tử UBND Xã Cẩm Thạch, Thanh Hóa, "Ứng dụng trí tuệ nhân tạo nâng cao hiệu quả cung cấp dịch vụ công," 2024. [Online]. Available: https://camthach.thanhhoa.gov.vn/chuyen-doi-so/ung-dung-tri-tue-nhan-tao-nang-cao-hieu-qua-cung-cap-dich-vu-cong-563842.
[21] Cổng TTĐT Chuyển đổi số tỉnh Lào Cai, "Dân vùng khó khăn dễ dàng thực hiện thủ tục hành chính với Dịch vụ công AI," 2024. [Online]. Available: https://chuyendoiso.laocai.gov.vn/tin-trong-nuoc/dan-vung-kho-khan-de-dang-thuc-hien-thu-tuc-hanh-chinh-voi-dich-vu-cong-ai-1306172.
[22] Cổng thông tin điện tử Bộ Xây dựng, "Bộ Xây dựng triển khai Tổng đài thông minh ứng dụng AI hỗ trợ thủ tục hành chính," 2025. [Online]. Available: https://moc.gov.vn/vn/tin-tuc/1305/85741/bo-xay-dung-trien-khai-tong-dai-thong-minh-ung-dung-ai-ho-tro-thu-tuc-hanh-chinh.aspx.
[23] Y. Du et al., "PP-OCR: A practical ultra lightweight OCR system," arXiv preprint arXiv:2009.09941, 2020.
[24] P. B. C. Quoc, "VietOCR: A transformer-based OCR for Vietnamese," GitHub repository, 2021. [Online]. Available: https://github.com/pbcquoc/vietocr.
[25] ProtonX, "Giáo trình Xử lý Ngôn ngữ Tự nhiên (NLP) ứng dụng: Kỹ thuật tiền xử lý dữ liệu tiếng Việt," ProtonX AI Training Platform, 2024. [Online]. Available: https://protonx.io/.
[26] J. Johnson, M. Douze, and H. Jégou, "Billion-scale similarity search with GPUs," IEEE Transactions on Big Data, vol. 7, no. 3, pp. 535-547, 2019.
[27] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems, vol. 33, pp. 9459-9474, 2020.
[28] J. Chen et al., "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," arXiv preprint arXiv:2402.03216, 2024.





























[29] L. Wang, N. Yang, X. Huang, B. Jiao, L. Yang, D. Jiang, R. Majumder, and F. Wei, "Text embeddings by weakly-supervised contrastive pre-training," arXiv preprint arXiv:2212.03533, 2022.

PHỤ LỤC
Bản sao thuyết minh đề tài đã được phê duyệt.
Bản sao các công trình khoa học đã được công bố trong thời gian nghiên cứu bao gồm trang bìa, mục lục và toàn văn công trình (nếu có).

