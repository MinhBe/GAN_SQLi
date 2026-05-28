Trần Quý Nam
Tóm tắt: Ảnh các nhân vật Pokemon có tính chất nhân
tạo, mang tính hoạt hình nên khác với các bài toán xử lý
ảnh thông thường. Nghiên cứu này thử nghiệm, đánh giá
khả năng đáp ứng của mô hình mạng học sâu GAN
(Generative Adversarial Networks) đối với tập ảnh các
nhân vật Pokemon. Mô hình sử dụng mạng nơ ron tích
chập cho phần phân biệt và mạng nơ ron giải chập cho
phần sinh dữ liệu ảnh nhân vật Pokemon. Tập dữ liệu thử
nghiệm là bộ ảnh Veekun. Kết quả thử nghiệm cho thấy,
dù là hình ảnh trò chơi nhưng mô hình GAN vẫn có khả
năng áp dụng khá phù hợp, có tiềm năng ứng dụng cho
bài toán sinh dữ liệu đa phương tiện.
Từ khóa: GAN, Pokemon, mô hình sinh, mô hình
phân biệt, ảnh thật, ảnh giả.
I. GIỚI THIỆU
Ngành công nghệ đa phương tiện hiện nay đang phát
triển đa dạng với sự phát triển sản phẩm Games, thực tế
ảo (VR), thực tế ảo tăng cường (AR), thực tế hỗn hợp
(MR), thực tế ảo mở rộng Extended Reality (XR)…
Metaverse xuất hiện, thể hiện một xu thế phát triển các
công nghệ ảo hóa và mở ra không gian lớn cho hoạt động
nghiên cứu và ứng dụng. Trò chơi Pokemon Go là một
trong các ví dụ sử dụng các công nghệ ảo hóa này.
Hiện nay, trò chơi Pokemon có hữu hạn nhân vật
(khoảng 800) hình ảnh đồ họa (Hình 1). Quá trình nâng
cấp trò chơi, phát triển kịch bản, cần các nhân vật mới.
Trong khi đó, việc vẽ thủ công, dùng đồ họa máy tính
thông thường bị giới hạn khả năng tăng số lượng nhân vật
và tính đa dạng của nhân vật, chưa tự động kế thừa các
đặc tính của nhân vật cũ. Đồng thời, nhà phát triển games
muốn thăm dò thị hiếu người chơi với dự kiến hình ảnh
nhân vật mới thì việc tự động hóa, tốn ít chi phí trong tạo
hình nhân vật đóng một vai trò nhất định. Để phát triển
mở rộng trò chơi Pokemon, việc tự động tạo thêm các
nhân vật trò chơi ít tốn kém chi phí thông qua mạng GAN
sẽ đóng góp một hướng nghiên cứu tiềm năng trong công
nghiệp trò chơi.
Mô hình GAN (Generative Adversarial Networks) do
Goodfellow và cộng sự đưa ra năm 2014 [1]. GAN là mô
hình sinh dữ liệu, nghĩa là mô hình có khả năng sinh ra dữ
liệu mới từ tập dữ liệu đầu vào có các đặc điểm tương tự.
Hình 1: Nhân vật Pokemon
Những năm gần đây, có nhiều thử nghiệm với ứng
dụng thay đổi tuổi của khuôn mặt, thay đổi độ tuổi của
khuôn mặt người nào đó. Dựa trên khuôn mặt của con
người hiện tại, GAN sẽ sinh ra các biến thể theo từng độ
tuổi của con người. Trên thực tế, có thể thử nghiệm các
ứng dụng này trên các mạng xã hội như Instagram,
TikTok... Các ứng dụng đó tạo ra những ảnh mặt người
già nua đi sau vài năm tới và hình ảnh tiến hóa này có thể
được sinh ra bởi GAN, không phải mặt người thật. Dữ
liệu sinh ra nhìn như thật nhưng không phải là ảnh thật.
GAN chứa hai mạng nơ-ron riêng biệt, một mạng nơ-ron
đóng vai trò sinh dữ liệu (Generator) và một mạng nơ-ron
khác đóng vai trò phân biệt (Discriminator). Đầu tiên, bộ
phận sinh dữ liệu tạo ra các hình ảnh ngẫu nhiên và bộ
phận phân biệt sẽ đánh giá những hình ảnh đó và cho bộ
phận sinh đã tạo ra dữ liệu đó biết mức độ chân thực của
các hình ảnh được tạo ra. Discriminator sẽ là đối thủ của
Generator được cung cấp cùng lúc với cả hình ảnh được
sinh ra cũng như loại hình ảnh gốc cho phép
Discriminator phân biệt. Sau khi đạt đến một điểm nhất
định, bộ phận phân biệt (Discriminator) sẽ không thể biết
được hình ảnh tạo ra bởi bộ phận sinh (Generator) là ảnh
thật hay ảnh giả, khi đó mô hình tốt, sinh dữ liệu giả
giống như thật. Trên thực tế, chất lượng của những ứng
dụng GAN áp dụng trên khuôn mặt ngày càng tốt hơn qua
từng năm.
Mặc dù có phạm vi ứng dụng hẹp, nhưng bài toán sinh
ảnh (generating images) vẫn có ý nghĩa thực tiễn nhất
định. Trong ngành công nghiệp phim hoạt hình Nhật Bản,
đã có một số bài báo trình bày tiềm năng ứng dụng mạng
GAN để tạo nhân vật hoạt hình cho nhân vật hoạt hình có
tên là Anime [10]. Thay vì sử dụng các họa sỹ, sử dụng
nhân lực thủ công và tốn nhiều chi phí, tốn công sức để
Trần Quý Nam
Đại học Đại Nam
ỨNG DỤNG MẠNG GAN TRONG BÀI
TOÁN SINH DỮ LIỆU ĐA PHƯƠNG TIỆN
Tác giả liên hệ: Trần Quý Nam,
Email: namtq.dn@gmail.com
Đến tòa soạn: 12/2022, chỉnh sửa: 02/2023, chấp nhận đăng:
03/2023.
SOÁ 01 (CS.01) 2023
TAÏP CHÍ KHOA HOÏC COÂNG NGHEÄ THOÂNG TIN VAØ TRUYEÀN THOÂNG 74


---

ỨNG DỤNG MẠNG GAN TRONG BÀI TOÁN SINH DỮ LIỆU ĐA PHƯƠNG TIỆN

thuê nghệ sĩ vẽ tranh, mạng GAN có thể hỗ trợ cách làm
việc hiệu quả hơn nghệ sĩ vẽ tranh trong lĩnh vực này.
Trong công nghiệp thời trang, để thăm dò thị trường,
thử thị hiếu người tiêu dùng trước đối với các sáng tạo
mẫu mã quần áo mới, GAN được áp dụng để sinh ra hình
ảnh mẫu mã mới mà không cần làm mẫu sản phẩm trước,
giúp tiết kiệm chi phí và có nhiều mẫu mã thăm dò mới.
Sohn và cộng sự [13] đã xem xét đánh giá của người tiêu
dùng về giá trị tiêu dùng sản phẩm, ý định mua hàng và
mức độ sẵn sàng chi trả cho các sản phẩm thời trang được
thiết kế bằng cách sử dụng mạng GAN. Nghiên cứu này
khám phá sự khác biệt giữa đánh giá của người tiêu dùng
về sản phẩm tạo ra bởi GAN và sản phẩm không tạo ra
bởi GAN và kiểm tra xem việc sử dụng công nghệ GAN
có ảnh hưởng đến đánh giá của người tiêu dùng hay
không.
GAN là một trong những xu hướng nghiên cứu thu hút
được đông đảo các nhà khoa học, có tính ứng dụng cao và
phát triển mạnh mẽ trong những năm gần đây trong ứng
dụng kỹ thuật học sâu. Mô hình GAN gần đây đã đạt
được một số kết quả ấn tượng cho nhiều ứng dụng trong
thế giới thực và nhiều biến thể GAN đã xuất hiện với
những cải tiến về chất lượng mẫu và độ ổn định đào tạo.
GAN được ứng dụng rộng rãi trong các bài toán thực tế,
cho cả bài toán phân loại và hồi quy, cho kết quả tốt. Bên
cạnh kiến trúc GAN đầu tiên được Ian GoodFellow giới
thiệu vào năm 2014, trong những năm qua, một số kiến
trúc GAN nâng cao hơn đã ra đời, đưa lại nhiều lợi ích
cho các ứng dụng thực tế như CycleGAN, StyleGAN...
II. CÁC NGHIÊN CỨU ĐÃ ỨNG DỤNG GAN
Thực tế đã có rất nhiều nghiên cứu sử dụng mô hình
GAN trên thế giới. Một trong số đó là nghiên cứu do
Islam và cộng sự [2] thực hiện đã cho thấy mô hình GAN
làm việc hiệu quả với bộ dữ liệu hình ảnh y tế với tập dữ
liệu hạn chế và số lượng nhỏ các mẫu. Điều này chỉ ra
tiềm năng sử dụng GAN để phát triển một mô hình chẩn
đoán bệnh thông qua các hình ảnh y tế tổng hợp bằng
cách sử dụng mạng GAN. Năm 2016, Olof đã ứng dụng
mạng GAN để đào tạo hiệu quả các mạng nơron học sâu
cho âm nhạc [3]. Đây là một mô hình đối nghịch hoạt
động dựa trên dữ liệu tuần tự liên tục và áp dụng GAN
bằng cách đào tạo trên một bộ dữ liệu âm nhạc cổ điển.
Nghiên cứu kết luận rằng GAN tạo ra âm thanh ngày càng
hay hơn khi mô hình được đào tạo và cho phép người
nghe đánh giá chất lượng bằng cách tải xuống các bài hát
đã tạo.
Tero và cộng sự [4] đã tạo ra khuôn mặt người thông
qua mô hình GAN. Trong đó có khả năng tạo ra những
khuôn mặt nhân tạo mà rất khó phân biệt với người thật.
Nghiên cứu của Antipov [5] đã sử dụng mạng GAN để
tạo ra hình ảnh tổng hợp có độ trung thực cao. Trong
nghiên cứu đó đã đề xuất phương pháp dựa trên GAN để
tự động hóa quá trình lão hóa khuôn mặt [5]. Kết quả
nghiên cứu đã đánh giá khách quan các hình ảnh khuôn
mặt trẻ hóa và già nua thu được bằng các giải pháp ước
tính độ tuổi và nhận dạng khuôn mặt cho thấy tiềm năng
cao của phương pháp được đề xuất dựa trên mô hình
GAN. David và cộng sự [6] đã nghiên cứu sâu mạng
GAN để hình dung hoặc hiểu rõ xử lý các thể hiện thế
giới hình ảnh bên trong và nguyên nhân tạo ra kết quả
mạng GAN, các lựa chọn kiến trúc ảnh hưởng đến việc
học GAN. Từ đó giúp phát triển những hiểu biết sâu sắc
mới và các mô hình GAN tốt hơn. Trong nghiên cứu này,
các tác giả đã trình bày một khung phân tích để hình dung
và hiểu các tác động GAN ở cấp độ đơn vị, đối tượng và
cảnh, xác định một nhóm các đơn vị có thể diễn giải có
liên quan chặt chẽ đến các khái niệm đối tượng bằng cách
sử dụng phương pháp phân tích mạng dựa trên phân đoạn.
Sau đó, phân tích định lượng tác động nhân quả của các
đơn vị có thể diễn giải bằng cách đo lường khả năng can
thiệp kiểm soát các đối tượng trong đầu ra. Kết quả
nghiên cứu hiển thị một số ứng dụng thực tế được hỗ trợ
bởi khung công tác trên các đơn vị, từ việc so sánh các
biểu diễn nội bộ trên các lớp, mô hình và bộ dữ liệu khác
nhau, đến cải thiện GAN bằng cách định vị và loại bỏ các
đơn vị gây nhiễu, đến thao tác tương tác các đối tượng
trong một khung ảnh. Jianmin và cộng sự [7] đã ứng dụng
GAN để tổng hợp hình ảnh khuôn mặt của một người
hoặc các đối tượng cụ thể trong một danh mục và sử dụng
đối sánh đặc điểm theo từng cặp để giữ cấu trúc của hình
ảnh được tạo. Các tác giả thử nghiệm với các hình ảnh tự
nhiên về khuôn mặt, hoa và chim, và chứng minh rằng
các mô hình được đề xuất có khả năng tạo ra các mẫu
thực tế và đa dạng với các nhãn danh mục chi tiết. Kết
quả nghiên cứu còn cho thấy rằng các mô hình GAN có
thể được áp dụng cho các tác vụ, chẳng hạn như in hình
ảnh, độ phân giải siêu cao và dữ liệu tăng cường đào tạo
mô hình nhận dạng khuôn mặt tốt hơn.
Marra và cộng sự [8] đã sử dụng GAN để giải quyết
bài toán lan truyền của các hình ảnh và video giả trên
mạng xã hội. Các tác giả đã sinh hình ảnh nhờ các hình
ảnh khác, dựa trên kiến trúc mạng đối nghịch GAN.
Trong nghiên cứu đó, các tác giả đã nghiên cứu hiệu suất
của một số bộ phát hiện giả mạo hình ảnh chống lại quá
trình biến đổi từ ảnh sang ảnh, cả trong điều kiện lý tưởng
và khi ảnh bị nén, được thực hiện thường xuyên khi tải
lên mạng xã hội. Nghiên cứu, được thực hiện trên tập dữ
liệu gồm 36.302 hình ảnh, cho thấy độ chính xác phát
hiện lên đến 95% có thể đạt được bằng cả kỹ thuật học
máy truyền thống và học sâu, nhưng chỉ kỹ thuật học sâu
mới cung cấp độ chính xác cao, khoảng 89% trên dữ liệu
ảnh bị nén.
 Nghiên cứu trên các bức ảnh chụp phổi bệnh nhân
Covid-19 sử dụng mô hình GAN đã cho thấy tiềm năng
chẩn đoán hình ảnh X-Quang bệnh nhân nhiễm Covid-19.
Nghiên cứu [9] mở ra hướng mới trong ứng dụng trí tuệ
SOÁ 01 (CS.01) 2023
TAÏP CHÍ KHOA HOÏC COÂNG NGHEÄ THOÂNG TIN VAØ TRUYEÀN THOÂNG 75


---

Trần Quý Nam

nhân tạo trong chẩn đoán hình ảnh chụp phổi các bệnh
nhân Covid-19.
III. MÔ HÌNH LÝ THUYẾT MẠNG GAN
Dựa trên cơ sở lý thuyết mô hình GAN của
Goodfellow và cộng sự đưa ra năm 2014 [1], bài toán này
áp dụng cho tập dữ liệu hình ảnh Pokemon. Vì vậy, mô
hình GAN áp dụng thử nghiệm sử dụng mạng nơ ron tích
chập (Convolutional Neural Network) cho Discriminator
và giải tích chập (Deconvolutional Neural Network) cho
Generator (Hình 2). Mô hình GAN sẽ có hai bộ phận
chính: Generator (G) và Discriminator (D). Trong đó, G
có chức năng sinh ra ảnh Pokemon giả và D làm nhiệm vụ
phân biệt một bức ảnh Pokemon là ảnh thật hay ảnh giả.
Về bản chất, Generator học cách sinh ra dữ liệu giả để lừa
mô hình Discriminator. Để có thể đánh lừa được
Discriminator thì đòi hỏi mô hình sinh ra các bức ảnh
Pokemon phải thực sự tốt. Do đó chất lượng ảnh
Pokemon phải càng như thật càng tốt. Trong khi đó,
Discriminator sẽ học cách phân biệt giữa dữ liệu ảnh
Pokemon giả được sinh từ mô hình Generator với dữ liệu
thật. Discriminator như một bộ lọc giám sát đánh giá kết
quả của Generator xem liệu mạng nơ ron này đã sinh dữ
liệu đã đạt chất lượng tốt để qua đánh lừa được
Discriminator chưa và nếu chưa thì Generator cần tiếp tục
phải học để tạo ra ảnh Pokemon giống ảnh thật hơn. Đồng
thời, Discriminator cũng phải cải thiện khả năng phân biệt
của mình vì chất lượng ảnh được tạo ra từ Generator càng
ngày càng giống thật hơn. Thông qua quá trình huấn
luyện thì cả Generator và Discriminator cùng cải thiện
được khả năng của mình.
Generator và Discriminator tương tự như hai người
chơi trong bài toán trò chơi tổng bằng không trong lý
thuyết trò chơi. Ở trò chơi này thì hai người chơi xung đột
lợi ích, thiệt hại của người này chính là lợi ích của người
kia. Mô hình Generator tạo ra dữ liệu giả tốt hơn sẽ làm
cho Discriminator phân biệt khó hơn và khi Discriminator
phân biệt tốt hơn thì Generator cần phải tạo ra ảnh giống
thật hơn để Discriminator không phát hiện được. Trong
trò chơi tổng bằng không, mỗi người chơi sẽ có chiến
lược riêng của mình, đối với Generator thì đó là sinh ra
ảnh giống thật và Discriminator là phân loại chính xác
ảnh thật (real) và ảnh giả (fake). Sau các bước ra quyết
định của mỗi người chơi thì trò chơi tổng bằng không sẽ
đạt được cân bằng Nash tại điểm cân bằng (Nash
Equilibrium). Quá trình hoạt động của mạng là một quá
trình huấn luyện các trọng số cho mô hình 2 lớp trong một
trò chơi có tổng bằng không [12]. Trong quá trình truyền
nghịch, một lớp được dùng để tạo ra dữ liệu giả giống hệt
như dữ liệu thật. Trong khi đó, lớp còn lại là lớp kiểm tra
đóng vai trò đánh giá để phân biệt dữ liệu thật và dữ liệu
giả được tạo ra. Hình 2 minh họa kiến trúc của mạng
GAN sử dụng mạng tích chập cho Discriminator và mạng
giải chập cho Generator [14].

Hình 2: Mô hình mạng GAN [14]
Generator về bản chất là một mô hình sinh nhận đầu
vào là một tập hợp các véc tơ nhiễu z được khởi tạo ngẫu
nhiên theo phân phối Gaussian [1]. Từ tập véc tơ đầu
vào z ngẫu nhiên, mô hình Generator là một mạng học sâu
có tác dụng biến đổi ra bức ảnh giả ở đầu ra. Bức ảnh giả
này sẽ được sử dụng làm đầu vào cho kiến trúc
Discriminator.
Để xác định cách phân phối Pg của Generator trên dữ
liệu x, cần xác định biến đầu vào pz(z), sau đó biểu diễn
một ánh xạ tới không gian dữ liệu dưới dạng G(z; θg),
trong đó G là một hàm khả vi được đại diện bởi một mạng
nơ ron nhiều lớp (mạng giải chập) với các tham số θg.
Đồng thời cũng xác định một mạng nơ ron nhiều lớp thứ
hai D(x; θd) với đầu ra là một đại lượng vô hướng duy
nhất. D(x) đại diện cho xác suất x đến từ dữ liệu, không
phải Pg. Thực hiện huấn luyện D để tối đa hóa xác suất
gán đúng nhãn cho cả dữ liệu đào tạo và mẫu từ G. Đồng
thời đào tạo G để giảm thiểu lỗi:
L = log (1 - D(G(z))) (1)
Nói cách khác, D và G đóng vai trò là 2 người chơi trò
chơi đối nghịch nhau, cả G và D đều cố gắng tối ưu giá trị
của hàm. Định nghĩa sự tối ưu giá trị của V (G, D) như
sau:
min
G max
D
V(D, G) = E𝑥~𝑝𝑑𝑎𝑡𝑎(𝑥)[logD(x)]
+ E𝑧~𝑝𝑧(𝑧)[log (1 −D(G(z)))] (2)
Mô hình Discriminator sẽ có tác dụng phân biệt ảnh
đầu vào là thật hay giả. Nhãn của mô hình sẽ là thật nếu
ảnh đầu vào của Discriminator được lấy tập mẫu huấn
luyện và là giả nếu được lấy từ đầu ra của mô hình
Generator. Về bản chất đây là một bài toán phân loại nhị
phân (binary classification) thông thường nên để tính xác
suất cho đầu ra cho Discriminator sẽ sử dụng hàm
Sigmoid. Mục tiêu của pha huấn luyện Discriminator này
là huấn luyện một mô hình Discriminator sao cho khả
năng phân loại là tốt nhất. Ở pha này tạm thời coi các giá
trị trọng số của G không đổi và chỉ quan tâm đến
vế maxDV(D, G). Đây là chính là đối của hàm cross
entropy đối với trường hợp phân loại nhị phân. Mục tiêu
của hồi quy logistic đối với bài toán phân loại nhị phân
là tối thiểu hóa một hàm cross entropy như sau:
ℒ(𝑊; 𝑋, 𝑦) = −1
𝑁∑[y𝑖log 𝑝(y𝑖/x𝑖) + (1 −𝑦𝑖)log (1
𝑁
𝑖=1
−𝑝(y𝑖/x𝑖))] (3)
SOÁ 01 (CS.01) 2023
TAÏP CHÍ KHOA HOÏC COÂNG NGHEÄ THOÂNG TIN VAØ TRUYEÀN THOÂNG 76
