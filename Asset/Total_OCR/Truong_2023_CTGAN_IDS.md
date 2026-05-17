  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
1 
 
ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH – VIỆT NAM 
 
ĐẠI HỌC CÔNG NGHỆ THÔNG TIN 
---------- 
 
BÁO CÁO ĐỒ ÁN 
HỆ THỐNG TÌM KIẾM, PHÁT HIỆN VÀ NGĂN NGỪA XÂM NHẬP 
GAN-based imbalanced data intrusion detection system 
GIẢNG VIÊN HƯỚNG DẪN: ĐỖ HOÀNG HIỂN 
NT204.N21.ATCL – VN 
 
 
NHÓM 5: 
TRƯƠNG THỊ HOÀNG HẢO - 20520191 
NGUYỄN ĐỨC TRUNG - 20520956 
LÊ QUANG MINH - 20520245 
NGUYỄN VIỆT HOÀNG – 20520189 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
2 
MỤC LỤC 
 
I. GIỚI THIỆU ............................................................................................................................................ 3 
II. THIẾT KẾ VÀ CÀI ĐẶT...................................................................................................................... 3 
2.1 Thiết kế .............................................................................................................................................. 3 
2.2 Dataset ................................................................................................................................................ 4 
2.3 GAN .................................................................................................................................................... 5 
2.4 CTGAN .............................................................................................................................................. 5 
2.5 Rare resampling ................................................................................................................................ 6 
2.6 Classification ..................................................................................................................................... 6 
III. KẾT QUẢ.............................................................................................................................................. 7 
IV. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN......................................................................................... 10 
V. TÀI LIỆU THAM KHẢO ................................................................................................................... 11 
VI. PHÂN CHIA CÔNG VIỆC ............................................................................................................... 11 
 
 
 
 
 
 
 
 
 
 
 
 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
3 
I. GIỚI THIỆU 
Với sự phát triển của ngày càng nhanh của Công nghệ thông tin thì việc an toàn bảo mật 
mạng cũng ngày càng trở nên phức tạp. Các nhu cầu bảo vệ về thông tin các nhân cũng, 
cũng như các vụ tấn công mạng ngày càng gia tăng. Do đó các Hệ thống tìm kiếm, phát 
hiện và ngăn ngừa xâm nhập đã trở thành một phần không thể thiếu trong máy tính và an 
toàn mạng.  
Phát hiện xâm nhập là một biện pháp bảo mật giúp bảo vệ máy tính và hệ thống mạng khỏi 
khả năng khai thác. Hệ thống phát hiện xâm nhập phát hiện các bất thường thông qua nhiều 
phướng pháp, trong đó bao gồm dựa trên các signature-based, bằng việc so sánh với các 
mẫu tấn công đã được cấu hình từ trước. Ngoài ra ta còn có các phương pháp anomaly-
based và hybrid-based từ đó giúp gia tăng hiệu quả trong việc phát hiện các ngoại lệ 
Trong đó việc ứng dụng Machine Learning/Deep Learning với IDS cũng ngày càng được 
phổ biến bởi độ chính xác cao cũng như có thể tự động phát hiện các loại hình tấn công 
chưa được phát hiện. Việc ứng dụng Deep Learning vào các mô hình phân loại IDS cần sử 
dụng một lượng dữ liệu lớn, nên vì thế đối với các tập dữ liệu mất cân bằng, độ chính xác 
của mô hình sẽ giảm đáng kể. Đã có nhiều nghiên cứu trong việc giải quyết vấn đề mất cân 
bằng dữ liệu tuy nhiên phần lớn gặp điểm yếu trong việc mất dữ liệu hoặc overfitting.  
Ở đây nhóm đề xuất sử dụng phương pháp Generative Adversarial Network (GAN), mô 
hình học không giám sát để tạo ra một tập dữ liệu ảo tương tự với tập dữ liệu ban đầu và 
sử dụng mô hình Random Forest (RF) để đánh giá kết quả của mô hình so với việc có và 
không sử dụng GAN.  
II. THIẾT KẾ VÀ CÀI ĐẶT 
 
2.1 Thiết kế 
Mô hình của bài báo được thể hiện trong hình 1. Sau khi chuẩn hóa dataset, tập train và tập 
test chia lần lượt thành 60 và 40. Tập train được điều chỉnh sau khi rare class của tập train 
đã được học bởi GAN và tạo ra những mẫu mới. 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
4 
Tập train và tập dữ liệu ảo do mô hình GAN tạo ra sẽ được gộp lại thành một và đưa vào 
mô hình học máy RF để huấn luyện mô hình multilabel phát hiện tấn công. Mô hình sẽ 
được kiểm chứng bởi tập test. 
 
Hình 1: Mô hình đề xuất  
2.2 Dataset 
 Tập dữ liệu được sử dụng cho mô hình đề xuất là CICIDS 2017. Tập dữ liệu này bao gồm 
các traffic bình thường và 12 loại tấn công. Tỷ lệ dữ liệu tương tự như mạng trong thực tế, 
nơi mà các dữ liệu bình thường chiếm hơn 80% và có ít hơn 0.1% các class thiểu số như 
Infiltration, web attacks và Heartbleed attacks. 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
5 
2.3 GAN 
 GAN là mô hình sinh hồi quy được phát minh bởi Ian Goodfellow ở NIPS năm 2014. Về 
cơ bản, một mạng neuron gọi là G sẽ tạo ra dữ liệu mới tương đồng. Trong khi đó, mạng 
neuron D sẽ đánh giá tính xác thực của dữ liệu. G sẽ tạo ra một image mới để đánh lừa D. 
Mục đích của D là xác định image tạo ra từ G là giả. Điều này được minh họa trong hình 
2. 
 
Hình 2. Cấu trúc của GAN 
2.4 CTGAN  
Conditional GAN (CTGAN) là một phương pháp dựa trên GAN (Generative Adversarial 
Network) để mô hình hóa phân phối dữ liệu bảng và tạo ra mẫu từ phân phối đó. Mô hình 
này sử dụng phương pháp chuẩn hóa theo chế độ để xử lý sự phân phối không Gaussian và 
đa chế độ trong dữ liệu bảng. CTGAN thiết kế một bộ sinh có điều kiện và sử dụng huấn 
luyện bằng cách lấy mẫu để xử lý các cột rời rạc không cân bằng trong dữ liệu bảng. Mô 
hình CTGAN sử dụng mạng fully-connected và các kỹ thuật mới nhất để huấn luyện một 
mô hình chất lượng cao. 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
6 
 
Hình 3. Mô hình CTGAN 
Mô hình CTGAN sử dụng bộ sinh có điều kiện để tạo ra các hàng tổng hợp dựa trên một 
trong các cột rời rạc trong dữ liệu. 
Với huấn luyện bằng cách lấy mẫu, dữ liệu điều kiện và dữ liệu huấn luyện được lấy mẫu 
theo tần suất log của mỗi danh mục. Điều này giúp CTGAN khám phá đồng đều tất cả các 
giá trị rời rạc có thể có. 
CTGAN là một phương pháp ưu việt hơn GAN trong việc mô hình hóa và tổng hợp dữ liệu 
bảng/tabular. Với khả năng xử lý các biến rời rạc, phân phối phức tạp và đa chế độ, CTGAN 
cho phép tạo ra dữ liệu tổng hợp chất lượng cao và đa dạng hơn 
2.5 Rare resampling 
Sử dụng mô hình GAN, nghiên cứu này đã tạo ra 10.000 dữ liệu Bot, Infiltration và 
Heartbleed bổ sung, đây là các lớp hiếm gặp chỉ chiếm ít hơn 0,1% của bộ dữ liệu 
CICIDS2017. Batch_size là 500 và 300 epochs. Trong đó, Batch_Size là số lượng dữ liệu 
được học một lần còn Epoch hoàn thành việc học một lần cho toàn bộ bộ dữ liệu và kết 
quả tốt nhất đạt được khi epoch là 300. 
2.6 Classification 
Trong nghiên cứu này, mô hình RF, một thuật toán học máy điển hình, dùng để phân loại 
dựa trên dữ liệu mẫu tái tạo. Một ví dụ về ensemble learning là RF, mô hình này học từ 
nhiều mô hình học máy và dùng mô hình dự đoán để dự đoán giá trị tốt hơn là 1 model. RF 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
7 
là một thuật toán mà tạo ra nhiều cây quyết định (decision trees (DT)) và dự đoán lớp được 
chọn nhiều nhất giữa những giá trị được dự đoán trong mỗi cây. 
Không dễ dàng để tạo ra DT bởi vì nó phụ thuộc vào tập train. Đồng thời, vì phương pháp 
tiếp cận theo bậc, nếu có lỗi xảy ra trong quá trình phân loại thì phương pháp này sẽ không 
phù hợp cho việc phân loại  trong môi trường mạng do tính chất của lỗi sẽ lan truyền liên 
tục ở các bước tiếp theo. 
Trong thực nghiệm thì phân loại RF sử sụng thư viện của sklearn, thiết lập các siêu tham 
số Random_state = 1 và n_estimators = 100. Random_state sẽ cố định ngẫu nghiên hóa 
việc chọn biến để đạt được kết quả giống nhau trong các thí nghiệm, n_estimators chỉ số 
lượng DT. 
III. KẾT QUẢ  
Ở đây nhóm đánh giá kết quả của mô hình RF sau khi train dựa trên 4 tiêu chí được thể 
hiện trong hình 4. Kết quả của từng tiêu chí được thể hiện ở bảng 1.  
 
Hình 4: Các tiêu chí để đánh giá mô hình RF 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
8 
 
Bảng 1: Kết quả của hai mô hình (1) và (2) 
 
 
Flow Type 
0 
BENIGN 
1 
DDoS Hulk 
2 
DdoS 
Golden Eye 
3 
DoS 
Slowloris 
4 
DoS 
Slowhttptest 
5 
DDoS 
6 
PortScan 
7 
FTP-Patator 
8 
SSH-Patator 
9 
Web Attack 
10 
Bot 
11 
Infiltration 
12 
Heartbleed 
Bảng 2: Bảng đánh số cho từng loại tấn công trong tập CICIDS2017 
Model 
Accuracy 
(%) 
Precision 
Recall 
F1-score 
RF – SMOTE & RandomOversampling (1) 
99.85 
0.9986 
0.9985 
0.9986 
RF - CTGAN (2) 
99.87 
0.9986 
0.9987 
0.9986 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
9 
Kết quả phân loại cụ thể của từng label (được đánh số ở bảng 2) sẽ được thể hiện lần lượt 
qua confusion matrix ở hình 5 và hình 6 khi sử dụng model (1) và model (2). Số mẫu phân 
loại không đúng của model (1) là 1588 mẫu còn model (2) là 1458 mẫu. 
 
Hình 5: Confusion matrix của model RF-SMOTE 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
10 
 
Hình 6: Confusion matrix của model RF-CTGAN 
Dựa vào kết quả thu được, mô hình sử dụng CTGAN để tạo mẫu ảo có khả năng nhận diện 
hai loại tấn công là “Bot” và “Infiltration” còn thấp. Lượng dữ liệu do hai loại tấn công này 
cung cấp trong tập train không đủ để thoả mãn yêu cầu của mô hình CTGAN. Vì thế, chất 
lượng của các mẫu cho cả ba loại tấn công tạo ra bằng CTGAN chỉ đạt mức 76.29% so với 
các mẫu thật. Tuy nhiên, mô hình (2) đã thu được kết quả tốt hơn về mặt tổng quan và cũng 
không làm mất dữ liệu như khi sử dụng kĩ thuât Random Undersampling kết hợp với 
SMOTE ở mô hình (1). 
IV. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN 
Nghiên cứu này sử dụng mô hình GAN để tái tạo mẫu của một vài lớp thiểu số nhằm tái 
tạo chúng với độ chính xác cao. Số lượng dữ liệu của các lớp hiếm Bot, Infiltration và 
Heartbleed được huấn luyện bằng GAN và tăng dữ liệu của mỗi lớp lên 10000 mẫu để đánh 
giá hiệu năng phân loại. Kết quả thử nghiệm cho thấy hiệu năng phân loại với Random 


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
11 
Forest sau khi tái tạo mẫu bằng GAN tốt hơn so với mô hình Random Forest kết hợp với 
SMOTE và Random Undersampling. 
Mặc dù SMOTE và GAN có tương đồng trong việc tạo ra dữ liệu nhưng SMOTE có vấn 
đề về các lớp chồng lên nhau và bị nhiễu. Do đó, kết quả của mô hình GAN (tái tạo lại lớp 
hiếm và so sánh chính xác các thuộc tính) hiệu quả hơn trong việc xử lý dữ liệu mất cân 
bằng, giảm thiểu mất mát trong dữ liệu. 
Trong tương lai, IDS có thể được tăng cường, tăng tốc độ bằng cách thêm mô hình 
autoencoder nhằm nén các thuộc tính dữ liệu xuống level thấp trước khi tái tạo mẫu với 
GAN, hay cải thiện độ chính xác của các mẫu được tạo ra bởi GAN để tăng khả năng nhận 
diện của mô hình. 
V. TÀI LIỆU THAM KHẢO 
[1] L. Xu, M. Skoularidou, A. Cuesta-Infante, and K. Veeramachaneni, “Modeling tabular 
data using conditional gan. arxiv 2019,” arXiv preprint arXiv:1907.00503, vol. 1, 1907. 
[2] J. Lee and K. Park, “Gan-based imbalanced data intrusion detection system,” Personal 
and Ubiquitous Computing, vol. 25, pp. 121–128, 2021. 
VI. PHÂN CHIA CÔNG VIỆC 
TRƯƠNG THỊ HOÀNG HẢO - 
20520191 
Tạo dữ liệu bằng CTGAN, dựng mô hình (2). 
NGUYỄN ĐỨC TRUNG - 20520956 
Feature engineering tập dữ liệu, dựng mô hình (1). 
LÊ QUANG MINH - 20520245 
Tìm hiểu vể CTGAN, viết báo cáo 
NGUYỄN VIỆT HOÀNG - 20520189 
Tìm hiểu về CTGAN, viết báo cáo 
                


---

  
Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập 
  
 Project Report 
 Group 5  
  
 
 
 
12 
------------------------HẾT------------------------- 
Xin cảm ơn! 
 
 
 
 
