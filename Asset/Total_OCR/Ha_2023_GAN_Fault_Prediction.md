 
 
ĐẠI HàC ĐÀ N¾NG 
TR¯ỜNG ĐẠI HàC CÔNG NGHÞ THÔNG TIN VÀ TRUYÞN THÔNG VIÞT-HÀN 
 
 
 
 
BÁO CÁO TỔNG KẾT 
ĐÞ TÀI KHOA HàC VÀ CÔNG NGHÞ CẤP C¡ SỞ 
 
 
 
 
 
 
 
NGHIÊN CĀU CÁC MÔ HÌNH GAN (GENERATIVE ADVERSARIAL 
NETWORK) XỬ LÝ MẤT CÂN BẰNG DỮ LIÞU TRONG DỰ ĐOÁN 
LỖI PHẦN MÞM 
 
Mã số: ĐHVH-2023-03 
 
 
 
 
 
 
 
 
Chÿ nhißm đß tài: ThS. Hà Thß Minh Ph°¢ng 
 
 
 
 
 
 
 
 
 
 
 
 
Đà N¿ng, 12/2023 


---

 
 
ĐẠI HàC ĐÀ N¾NG 
  
TR¯ỜNG ĐẠI HàC CÔNG NGHÞ THÔNG TIN VÀ TRUYÞN THÔNG VIÞT-HÀN 
 
 
 
 
 
BÁO CÁO TỔNG KẾT  
 
ĐÞ TÀI KHOA HàC VÀ CÔNG NGHÞ  
CẤP C¡ SỞ 
 
 
 
 
 
 
 
NGHIÊN CĀU CÁC MÔ HÌNH GAN (GENERATIVE ADVERSARIAL   
NETWORK) XỬ LÝ MẤT CÂN BẰNG DỮ LIÞU TRONG DỰ ĐOÁN  
LỖI PHẦN MÞM 
 
 
 
Mã số: ĐHVH-2023-03  
 
 
 
 
 
 
Xác nhận cÿa c¢ quan chÿ trì đß tài               Chÿ nhißm đß tài        
 
 
                                        
                                                  
 
 
 
 
 
 
 
 
 
 
 
Đà N¿ng, 12/2023


---

Mục lục
Danh sách hình vẽ
3
Danh sách bảng
4
1
Tổng quan đềtài
1
2
Dựđoán lỗi phần mềm
5
2.1
Tổng quan vềdựđoán lỗi phần mềm . . . . . . . . . . . . . . . . . .
5
2.2
Quy trình dựđoán lỗi phần mềm . . . . . . . . . . . . . . . . . . . .
6
2.3
Độđo phần mềm
. . . . . . . . . . . . . . . . . . . . . . . . . . . . .
8
2.4
Lựa chọn đặc trưng . . . . . . . . . . . . . . . . . . . . . . . . . . . .
10
2.4.1
Lựa chọn đặc trưng dựa trên Filter . . . . . . . . . . . . . . .
10
2.4.2
Lựa chọn đặc trưng dựa trên Wrapper . . . . . . . . . . . . .
11
2.4.3
Lựa chọn đặc trưng dựa trên Embedded . . . . . . . . . . . .
11
2.5
Các mô hình học máy . . . . . . . . . . . . . . . . . . . . . . . . . . .
12
3
Các nghiên cứu liên quan
13
4
Mô hình GAN cho lấy mẫu dữliệu trong dựđoán lỗi phần mềm 14
4.1
Mô hình mạng GAN
. . . . . . . . . . . . . . . . . . . . . . . . . . .
14
4.2
VanillaGAN
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
15
4.3
Conditional GAN - CTGAN . . . . . . . . . . . . . . . . . . . . . . .
16
4.4
Wasserstein GAN With Gradient Penalty - WGANGP
. . . . . . .
17
5
Thực nghiệm đềxuất
17
5.1
Thực nghiệm dựa trên kết hợp giữa kỹthuật lựa chọn đặc trưng
dựa trên Filter (Filter-based feature selection) và các kỹthuật lấy
mẫu GAN
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
18
5.2
Thực nghiệm dựa trên kết hợp giữa kỹthuật lựa chọn đặc trưng
dựa trên Wrapper (wrapper-based feature selection) và các kỹthuật
lấy mẫu GAN . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
18


---

5.3
Tập dữliệu thực nghiệm . . . . . . . . . . . . . . . . . . . . . . . . .
20
5.4
Độđo đánh giá
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
21
5.5
Kết quảthực nghiệm . . . . . . . . . . . . . . . . . . . . . . . . . . .
24
5.5.1
Kết quảthực nghiệm 1 . . . . . . . . . . . . . . . . . . . . . .
25
5.5.2
Kết quảthực nghiệm 2 . . . . . . . . . . . . . . . . . . . . . .
27
6
Kết luận
29
References
31


---

Danh sách hình vẽ
1
Quy trình dựđoán lỗi phần mềm. . . . . . . . . . . . . . . . . . . . .
7
2
Mô hình kết hợp giữa kỹthuật lựa chọn đặc trưng dựa trên Filter
và các kỹthuật lấy mẫu GAN.
. . . . . . . . . . . . . . . . . . . . .
19
3
Mô hình kết hợp giữa kỹthuật lựa chọn đặc trưng dựa trên Wrapper
và các kỹthuật lấy mẫu GAN.
. . . . . . . . . . . . . . . . . . . . .
20


---

THÔNG TIN KÀT QUÀ NGHIÊN CĀU 
 
Đ¾I HâC ĐÀ NÀNG 
TR¯äNG Đ¾I HàC CÔNG NGHÞ THÔNG TIN VÀ 
TRUYÀN THÔNG VIÞT HÀN 
 
CàNG HÒA XÃ HàI CHĂ NGHĨA VIÞT NAM 
Đác lập – Tă do  - H¿nh phúc 
 
 
THÔNG TIN K¾T QUÀ NGHIÊN CĄU 
1. Thông tin chung: 
- Tên đề tài: Nghiên cąu các mô hình generative adversarial network (gan) xÿ 
lý mÃt cân bÁng dā lißu trong dă đoán lßi phÅn mÁm. 
- Mã số: ĐHVH-2023-03 
- Chÿ nhiệm: HÀ THà MINH PH¯¡NG 
- Thành viên tham gia:  
- C¢ quan chÿ trì: Khoa Khoa hãc máy tính – Tr°ờng ĐH CNTT&TT Việt - Hàn 
– Đ¿i hãc Đà NÁng 
- Thời gian thực hiện: từ tháng 5/2023 đÁn tháng 12/2023 
2. Māc tiêu: 
Nghiên cāu lý thuyÁt: 
 Nghiên cāu mô hình Generative adversarial networks (GANs) 
 Nghiên cāu các biÁn thể GANs để áp dụng vào việc bằng dữ liệu: 
VanillaGAN, CTGAN, WGANGP, CopullaGAN và TabularGAN 
 Nghiên cāu các mô hình máy hãc thực hiện dự đoán lỗi  
Nghiên cāu và áp dụng các biÁn thể cÿa GANs nói trên để đ°a vào xử lý mất cân 
bằng dữ liệu nhằm giÁi quyÁt vấn đề overfitting nâng cao độ chính xác cÿa mô hình 
dự đoán lỗi. Đồng thời, tiÁn hành thực nghiệm để so sánh hiệu quÁ cÿa các mô hình 
GANs trên và các kỹ thuật truyền thống nh° SMOTE, ADASYN, Border-SMOTE, 
Random Undersampling trong việc xử lý vấn đề mất cân bằng dữ liệu trong dự đoán 
lỗi phần mềm.  
3. Tính mãi và sáng t¿o: 
- Lỗi phần mềm s¿ tác động m¿nh đÁn các hệ thống phần mềm trong quá trình phát 
triển cũng nh° quá trình triển khai. 
- Để nâng cao chất l°ợng trong dự đoán lỗi phần mềm, tác giÁ đã nghiên cāu các 
kỹ thuật máy hãc, các kỹ thuật trong giai đo¿n tiền xử lý dữ liệu để xây dựng các 
mô hình dự đoán  Tuy nhiên, trong bộ dữ liệu lỗi phần mềm, các mô-đun bá lỗi 
(lo¿i thiểu số) đ¿i diện ít h¢n nhiều so với các mô-đun không bá lỗi (lo¿i đa số), 


---

THÔNG TIN KÀT QUÀ NGHIÊN CĀU 
 
đây là vấn đề mất cân bằng lo¿i. Do vấn đề này, hiệu suất cÿa các mô hình dự 
đoán lỗi bá cÁn trở nghiêm trãng. Nhiều nhà nghiên cāu đã cố gắng khắc phục 
vấn đề này cÿa mô hình dự đoán lỗi phần mềm. Do đó, các kỹ thuật lấy mẫu dữ 
liệu nh° oversampling và under-sampling đ°ợc sử dụng rộng rãi để giÁi quyÁt 
vấn đề mất cân bằng lớp trong dự đoán lỗi phần mềm. Các kỹ thuật oversampling 
t¿o ra các mô-đun lớp thiểu số để tăng số mẫu cÿa lớp thiểu số. Ng°ợc l¿i, các 
kỹ thuật under-sampling māc lo¿i bỏ một số mô-đun cÿa lớp đa số để cân bằng 
tỷ lệ các mô-đun cÿa lớp thiểu số và đa số. Tuy nhiên, một số nghiên cāu đã cho 
thấy các kỹ thuật sampling trên đã dẫn vấn đề các mô hình dự đoán bá overfitting. 
Trong những năm gần đây, mô hình GANs (Generative adversarial networks) đã 
đ°ợc nghiên cāu đề xuất để đ°a vào xử lý vấn đề mất cân bằng dữ liệu và giÁi 
quyÁt vấn đề overfitting cÿa mô hình dự đoán lỗi. Vì cậy, trong nghiên cāu này, 
chúng tôi tập trung nghiên đÁn mô hình GAN và các biÁn thể để xử lý vấn đề mất 
cân bằng dữ liệu trong dự đoán lỗi từ đó nâng cao hiệu quÁ dự đoán cÿa các mô 
hình. 
4. Tóm t¿t k¿t quÁ nghiên cąu: 
- Nghiên cāu đặc tr°ng phần mềm (metrics), vấn đề mất bằng dữ liệu trong dự 
đoán lỗi phần mềm. 
- Nghiên cāu các mô hình máy hãc trong dự đoán lỗi phần mềm. 
- Nghiên cāu các kỹ thuật cân bằng dữ liệu nh° SMOTE, ADASYN, Border-
SMOTE, RUS,... 
- Nghiên cāu và áp dụng mô hình GANs và các biÁn thể để đ°a vào cân bằng dữ 
liệu nhằm nâng cao hiệu suất cÿa mô hình dự đoán lỗi. 
- TiÁn hành thực nghiệm với các mô hình cÿa GANs cân bằng dữ liệu trên các tập 
dữ liệu trong kho dữ liệu Promise để đánh giá kÁt quÁ đ¿t đ°ợc và so sánh các kỹ 
thuật cân bằng dữ liệu truyền thống.  
5. Tên sÁn phẩm:  
- Báo cáo tổng kÁt đề tài; 
- Bài báo đăng trên hội thÁo CITA 2022 <Dự đoán lỗi phần mềm sử dụng 
Convolution Neural Network=; 
6. Hißu quÁ, ph°¢ng thąc chuyển giao k¿t quÁ nghiên cąu và khÁ năng áp dāng:  
- Về mặt giáo dục - đào t¿o: phục vụ công tác giÁng d¿y, nghiên cāu. 
- Về mặt khoa hãc: đóng góp đáng kể cÿa đề tài là nghiên cāu mô hình mới thực 
hiện dự đoán lỗi bằng phân tích ngữ nghĩa cÿa mã nguồn, qua đó có thể đề xuất đ°ợc 
các kỹ thuật máy hãc có tính hiệu quÁ và chính xác cao h¢n so với các mô hình dự đoán 
lỗi dựa trên độ đo mã nguồn. 


---

THÔNG TIN KÀT QUÀ NGHIÊN CĀU 
 
- Về sÁn phẩm āng dụng: đề xuất mô hình dự đoán lỗi và h°ớng tới áp dụng đ°ợc 
các hệ thống dự đoán đ°ợc lỗi phần mềm thực tÁ trong công nghệ phần mềm. 
 
7. Hình Ánh, s¢ đß minh háa chính: 
BÁng 1.  K¿t quÁ mô hình dă đoán lßi phÅn mÁm dă trên k¿t hÿp căa Chi-Squared and GAN 
 
 
 
BÁng 2. K¿t quÁ mô hình dă đoán lßi phÅn mÁm dă trên k¿t hÿp căa Information Gain và GAN 


---

THÔNG TIN KÀT QUÀ NGHIÊN CĀU 
 
 
BÁng 3. K¿t quÁ mô hình dă đoán lßi phÅn mÁm dă trên k¿t hÿp căa Fisher và GAN 
 
 
BÁng 4. K¿t quÁ mô hình dă đoán lßi phÅn mÁm dă trên k¿t hÿp căa Relief và GAN 
 
                                                                             Đà Nẵng, ngày    tháng     năm 2023 
C¢ quan chă trì 
                   Chă nhißm đÁ tài 
 
 
 
Hà Thß Minh Ph°¢ng


---

 
 
MỞ ĐÄU 
I. TàNG QUAN TÌNH HÌNH NGHIÊN CĄU THUàC LĨNH VĂC ĐÀ TÀI 
TRONG VÀ NGOÀI N¯âC 
1. Ngoài n°ãc 
a. Dă đoán lßi phÅn mÁm 
Trong bộ dữ liệu lỗi phần mềm, các mô-đun bá lỗi (lo¿i thiểu số) đ¿i diện ít h¢n 
nhiều so với các mô-đun không bá lỗi (lo¿i đa số), đây là vấn đề mất cân bằng lo¿i. Do 
vấn đề này, hiệu suất cÿa các mô hình dự đoán lỗi bá cÁn trở nghiêm trãng. Nhiều nhà 
nghiên cāu đã cố gắng khắc phục vấn đề này cÿa mô hình dự đoán lỗi phần mềm. Do 
đó, các kỹ thuật lấy mẫu dữ liệu nh° oversampling và under-sampling đ°ợc sử dụng 
rộng rãi để giÁi quyÁt vấn đề mất cân bằng lớp trong dự đoán lỗi phần mềm. Các kỹ 
thuật oversampling t¿o ra các mô-đun lớp thiểu số để tăng số mẫu cÿa lớp thiểu số. 
Ng°ợc l¿i, các kỹ thuật under-sampling māc lo¿i bỏ một số mô-đun cÿa lớp đa số để 
cân bằng tỷ lệ các mô-đun cÿa lớp thiểu số và đa số. Kameiet al.[1] đã đánh giá các 
ph°¢ng pháp lấy mẫu khác nhau (ROS, SMOTE, RUS và lựa chãn một phía) cho dự 
đoán lỗi bằng các kỹ thuật máy hãc khác nhau trong công việc cÿa hã. Các tác giÁ đã 
chß ra rằng các ph°¢ng pháp lấy mẫu giúp cÁi thiện hiệu suất cÿa các mô hình logistic 
và tuyÁn tính, trong khi các mô hình cây phân lo¿i và m¿ng thần kinh ho¿t động kém 
hiệu quÁ. Trong một nghiên cāu t°¢ng tự khác,Tanet al.[2] đã đánh giá bốn ph°¢ng 
pháp lấy mẫu (simple dupli-cate, spread subsample, SMOTE, and resampling 
with/withoutr eplacement). KÁt quÁ thử nghiệm cho thấy rằng ph°¢ng pháp resampling 
đ°ợc thực hiện tốt nhất trên toàn thÁ giới và các ph°¢ng pháp sampling đã cÁi thiện hiệu 
suất dự đoán. Các ph°¢ng pháp ensemble giÁi quyÁt vấn đề mất cân bằng lớp bằng cách 
t¿o và kÁt hợp một số mô hình yÁu để có đ°ợc mô hình m¿nh. Các ph°¢ng pháp tập hợp 
đ°ợc sử dụng phổ biÁn nhất là bag-ging, boost và stacking. Một số biÁn thể nh° Under-
Bagging, 
OverBagging, 
UnderOverBagging, 
SMOTEBagging,RUBoost 
và 
SMOTEBoost [3,4] đã đ°ợc áp dụng cho dự đoán lỗi. Tuy nhiên, một số nghiên cāu đã 
cho thấy các kỹ thuật sampling trên đã dẫn vấn đề các mô hình dự đoán bá overfitting. 
Trong những năm gần đây, mô hình GANs (Generative adversarial networks) đã đ°ợc 
nghiên cāu đề xuất để đ°a vào xử lý vấn đề mất cân bằng dữ liệu và giÁi quyÁt vấn đề 
overfitting cÿa mô hình dự đoán lỗi. Vì cậy, trong nghiên cāu này, chúng tôi tập trung 
nghiên đÁn mô hình GAN và các biÁn thể để xử lý vấn đề mất cân bằng dữ liệu trong dự 
đoán lỗi từ đó nâng cao hiệu quÁ dự đoán cÿa các mô hình. 
 [1] Kamei, A. Monden, S. Matsumoto, T. Kakimoto, and K.-I. Matsumoto,<The effects of over and 
under sampling on fault-prone module detection,= in Proc. 1st Int. Symp. Empirical Softw. Eng. 
Meas., 2007, pp. 196–204 


---

 
 
[2] M. Tan, L. Tan, S. Dara, and C. Mayeux, <Online defect prediction for imbalanced data,= inProc. 
IEEE/ACM 37th IEEE Int. Conf. Softw. Eng.,2015, pp. 99–108. 
[3] C. Seiffert, T. M. Khoshgoftaar, J. Van Hulse, and A. Napolitano, <RUS-boost: A hybrid approach 
to alleviating class imbalance,= IEEE Trans.Syst., Man, Cybern.-Part A, Syst. Humans, vol. 40, no. 
1, pp. 185–197,Jan. 2010 
[4] Z. Sun, Q. Song, and X. Zhu, <Using coding-based ensemble learning to improve software defect 
prediction,= IEEE Trans. Syst., Man, Cybern.,Part C, vol. 42, no. 6, pp. 1806–1817, Nov. 2012.  
2. Trong n°ãc 
Dự đoán lỗi phần mềm là một trong những giai đo¿n quan trãng để đÁm bÁo 
chất l°ợng cÿa phần mềm. Dự đoán lỗi phần mềm có thể xác đánh mô-đun lỗi 
trong phần mềm và phân lo¿i các lỗi. Các kiểm thử có thể tập trung kiểm tra các 
mô-đun đ°ợc dự đoán lỗi lỗi đó tr°ớc. Các dự án dự đoán lỗi truyền thống tập 
trung trên xây dựng các mô hình với các kỹ thuật máy hãc và độ đo (metrics). 
Các kỹ thuật hãc máy chÿ yÁu đã đ°ợc áp dụng  để phát triển các mô hình dự 
đoán lỗi phần mềm. Các kỹ thuật này sử dụng dữ liệu lỗi phần mềm lách sử (thu 
đ°ợc từ các dự án phần mềm tr°ớc đó) để huấn luyện các mô hình dự đoán và dự 
đoán các mô-đun bá lỗi. Trong quá trình huấn luyện, mô hình dự đoán thu đ°ợc 
kiÁn thāc về các đặc tr°ng cÿa dự án phần mềm và sử dụng kiÁn thāc này để dự 
đoán liệu mô-đun trong dự án khác có chāa lỗi hay không. Tuy nhiên, hầu hÁt 
các bộ dữ liệu lỗi lách sử bao gồm mô-đun không bá lỗi (tāc là lớp đa số) nhiều 
h¢n là các mô-đun bá lỗi (tāc là lớp thiểu số). Đây đ°ợc gãi là vấn đề cân bằng 
lớp trong dự đoán lỗi phần mềm. Nhiều kỹ thuật hãc máy giÁ đánh rằng tỷ lệ cÿa 
các mô-đun lớp thiểu số và mô-đun lớp đa số là xấp xß bằng nhau. Tuy nhiên, mô 
hình dự đoán đ°ợc xây dựng trên tập dữ liệu phần mềm mất cân bằng có khÁ 
năng không hãc đ°ợc các mẫu mô-đun bá lỗi và do đó có xu h°ớng dự đoán sai 
nhiều mô-đun bá lỗi. Điều này có thể dẫn đÁn các mô hình dự đoán không đáng 
tin cậy và không thể sử dụng trong thực tÁ. Vì vậy xử lý mất cân bằng dữ liệu 
trong dự đoán lỗi phần mềm đã đ°ợc tập trung nghiên cāu trong những năm qua. 
Nhiều nghiên cāu đã đề xuất các kỹ thuật xử lý mất cân bằng dữ liệu nh° data 
oversampling và data undersampling.  Trong quá trình tìm tài liệu tham khÁo 
bằng tiÁng Việt về dự đoán lỗi phần mềm, chúng tôi chß tìm thấy một bài báo thử 
nghiệm 3 kỹ thuật xử lý dữ liệu mất cân bằng dữ liệu [5] gồm: Random 
Undersampling, Random Oversampling và SMOTE. Các kỹ thuật đ°ợc áp dụng 
vào ba tập dữ liệu về dự báo lỗi cÿa NASA trong kho l°u trữ cÿa Promise. 
[5] Lê, Song Toàn, Thanh Bình Nguyễn, and Thá Mỹ H¿nh Lê, <Xử lý dữ liệu không cân bằng trong bài 
toán dự đoán lỗi phần mềm=, Kỷ yÁu Hội nghá KHCN Quốc gia lần thā XIII về Nghiên cāu c¢ bÁn và āng dụng 
Công nghệ thông tin (FAIR), 2020. 
 


---

 
 
II. TÍNH CÂP THI¾T CĂA ĐÀ TÀI 
CÁ hai bộ kỹ thuật Oversampling và Undersampling nhằm mục đích cân bằng việc 
biểu diễn các mô-đun lớp thiểu số và đa số để cÁi thiện hiệu suất cÿa các mô hình dự 
đoán. Đối với các kỹ thuật oversampling trong dự đoán lỗi phần mềm, các kỹ thuật nh° 
SMOTE và biÁn thể cÿa nó (ví dụ: ADASYN, Border-line_SMOTE) và Random 
Oversampling (ROS) hầu nh° đ°ợc sử dụng. Kỹ thuật ROS chß đ¢n giÁn là sao chép các 
mô-đun lớp thiểu số để cân bằng tập dữ liệu mà không cần thêm bất kỳ thông tin mới 
nào [6]. Điều này dẫn đÁn một mô hình dự đoán bá overfitting, có thể không ho¿t động 
chính xác đối với các mô-đun thử nghiệm khác. Các kỹ thuật dựa trên SMOTE t¿o ra 
các mô-đun lớp thiểu số tổng hợp bằng cách nội suy các mô-đun lân cận đã xác đánh 
(dựa trên khoÁng cách) để cân bằng tập dữ liệu [7,8]. Các mô-đun mới đ°ợc thêm này 
không phÁi là các mô-đun trùng lặp nh° trong ROS, nh°ng do các mô-đun lân cận, các 
kỹ thuật dựa trên SMOTE không thể t¿o ra các mô-đun lớp thiểu số đa d¿ng, điều này 
có thể dẫn đÁn việc overfitting cÿa nhiều mô hình dự đoán (hiệu suất thấp trên tập hợp 
con thử nghiệm). Vì vậy, chúng tôi tiÁn hành nghiên cāu về các mô hình GAN để thực 
hiện việc oversamling dữ liệu có tính đa d¿ng nhằm giÁi quyÁt vấn đề mất cân bằng lớp 
trong các mô hình dự đoán lỗi. 
[6] M. Hayaty, S. Muthmainah, and S. M. Ghufran, <Random and synthetic over-sampling approach 
to resolve data imbalance in classification,=Int.J. Artif. Intell. Res., vol. 4, no. 2, pp. 86–94, 2021. 
[7]  N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, <Smote: Synthetic minority over-
sampling technique,=J. Artif. Intell. Res., vol. 16,pp. 321–357, 2002. 
[8] H. Han, W.-Y. Wang, and B.-H. Mao, <Borderline-smote: A new over-sampling method in 
imbalanced data sets learning,= inProc. Int. Conf.Intell. Comput., 2005, pp. 878–887 
[9] H. He, Y. Bai, E. A. Garcia, and S. Li, <ADASYN: Adaptive synthetic sampling approach for 
imbalanced learning,= inProc. IEEE Int. Joint Conf.Neural Netw., 2008, pp. 1322–1328. 
III. MĀC TIÊU CĂA ĐÀ TÀI 
Nghiên cāu m¿ng GANs và các biÁn thể cÿa GANs nh° VanillaGAN, CTGAN, 
WGANGP, CopullaGAN và TabularGAN để t¿o ra các mẫu dữ liệu gần giống với 
phân phối dữ liệu lớp thiểu số ban đầu t°¢ng tự nh° các các kỹ thuật sampling truyền 
thống, ch¿ng h¿n nh° SMOTE. Tính đa d¿ng cũng có thể đ¿t đ°ợc khi các mẫu đã 
t¿o đ°ợc chãn dựa trên phân phối dữ liệu thay vì dựa trên khoÁng cách gần để sinh 
ra các mẫu dữ liệu. Từ đó, áp dụng các biÁn thể cÿa GANs nói trên để đ°a vào xử lý 
mất cân bằng dữ liệu nhằm giÁi quyÁt vấn đề overfitting nâng cao độ chính xác cÿa 
mô hình dự đoán lỗi. Đồng thời, tiÁn hành thực nghiệm để so sánh hiệu quÁ cÿa các 
mô hình GANs trên và các kỹ thuật truyền thống nh° SMOTE, ADASYN, Border-
SMOTE, Random Undersampling trong việc xử lý vấn đề mất cân bằng dữ liệu trong 
dự đoán lỗi phần mềm. 
     Nghiên cāu lý thuyÁt: 
 Nghiên cāu mô hình Generative adversarial networks (GANs) 


---

 
 
 Nghiên cāu các biÁn thể GANs để áp dụng vào việc bằng dữ liệu: 
VanillaGAN, CTGAN, WGANGP, CopullaGAN và TabularGAN 
 Nghiên cāu các mô hình máy hãc thực hiện dự đoán lỗi  
IV. ĐÞI T¯þNG VÀ PH¾M VI NGHIÊN CĄU 
1. Đßi t°ÿng nghiên cąu 
 Các kỹ thuật Oversampling và Undersampling để xử lý mất cân bằng dữ 
liệu trong dự đoán lỗi phần mềm. 
 Mô hình Generative adversarial networks  và các biÁn thể VanillaGAN, 
CTGAN, WGANGP, CopullaGAN và TabularGAN. 
 Các mô hình máy hãc nh° Random Forest, Extreme Gradient Boosting, 
Histogrambased Gradient Boosting, Multilayer Perceptron, Extra Trees, 
Adaptive Boosting. 
 Một số tập dữ liệu Apache. 
2. Ph¿m vi nghiên cąu 
Đề tài tập trung nghiên cāu các vấn đề sau: 
 Các mô hình hãc máy và hãc sâu áp dụng cho bài toán dự đoán lỗi phần 
mềm 
 Nghiên cāu các mô hình oversampling và undersampling áp dụng trong việc 
xử lý mất cân bằng dữ liệu 
 Nghiên cāu các mô hình m¿ng GAN để cân bằng dữ liệu 
 Xây dựng thực nghiệm để áp dụng các m¿ng GAN trong cân bằng dữ liệu 
cho các mô hình dự đoán lỗi phần mềm 
V. NàI DUNG NGHIÊN CĄU 
- Nghiên cāu đặc tr°ng phần mềm (metrics), vấn đề mất bằng dữ liệu trong dự 
đoán lỗi phần mềm. 
- Nghiên cāu các mô hình máy hãc trong dự đoán lỗi phần mềm. 
- Nghiên cāu các kỹ thuật cân bằng dữ liệu nh° SMOTE, ADASYN, Border-
SMOTE, RUS,... 
- Nghiên cāu và áp dụng mô hình GANs và các biÁn thể để đ°a vào cân bằng dữ 
liệu nhằm nâng cao hiệu suất cÿa mô hình dự đoán lỗi. 
- TiÁn hành thực nghiệm với các mô hình cÿa GANs cân bằng dữ liệu trên các tập 
dữ liệu trong kho dữ liệu Promise để đánh giá kÁt quÁ đ¿t đ°ợc và so sánh các kỹ 
thuật cân bằng dữ liệu truyền thống.  
- ViÁt báo cáo tổng kÁt. 


---

Danh sách bảng
1
Kết quảmô hình dựđoán lỗi phần mềm không áp dụng kỹthuật
lấy mẫu và lựa chọn đặc trưng . . . . . . . . . . . . . . . . . . . . . .
21
2
Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Chi-
Squared and GAN. . . . . . . . . . . . . . . . . . . . . . . . . . . . .
22
3
Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Infor-
mation Gain và GAN.
. . . . . . . . . . . . . . . . . . . . . . . . . .
25
4
Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Fisher
và GAN. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
26
5
Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Relief
và GAN. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
27
6
Kết quảso sánh của kết hợp các kỹthuật lựa chọn đặc trưng dựa
trên Wrapper và kỹluật lấy mẫu VanillaGAN. . . . . . . . . . . . .
28
7
Kết quảso sánh của kết hợp các kỹthuật lựa chọn đặc trưng dựa
trên Wrapper và kỹluật lấy mẫu VanillaGAN (tt). . . . . . . . . . .
29


---

1
Tổng quan đềtài
Một lỗi trong hệthống phần mềm được mô tảlà một sai sót cấu trúc có thểgây
ra hệthống bịlỗi trong tương lai. Dựđoán lỗi phần mềm là một hoạt động quan
trọng và cần thiết đểtăng chất lượng phần mềm và giảm thiểu nỗlực bảo trì trong
các giai đoạn ban đầu của phát triển phần mềm. Dựđoán lỗi sớm có thểdẫn đến
việc giải quyết kịp thời những lỗi này và cung cấp phần mềm có khảnăng bảo trì
tốt. Dựđoán lỗi phần mềm giúp cải thiện chất lượng phần mềm, trong đó các lỗi
được dựđoán dựa trên kiến thức trước đó dưới dạng các tập dữliệu. Có các kỹ
thuật Khai Phá Dữliệu (Data Mining), Máy Học (Machine Learning) và Học Sâu
(Deep Learning) mà chúng ta sửdụng đểdựđoán lỗi. Những kỹthuật này được
sửdụng đểxây dựng các mô hình có thểdùng đểdựđoán các lớp có lỗi và không
có lỗi.
Dựđoán Lỗi Phần mềm (Software Fault Prediction - SFP) được thực hiện
bằng cách phân chia các mô-đun/lớp thành các loại dễlỗi và không lỗi. Chúng ta
sửdụng các tập dữliệu lỗi từcác dựán tương tựhoặc các bản cập nhật trước
của các hệthống phần mềm. Sau đó, chúng ta áp dụng các mô hình đã phát triển
vào các mô-đun, lớp hoặc phương thức của các dựán phần mềm hiện tại, và phân
loại chúng là mô-đun, lớp hoặc phương thức dễlỗi hoặc không lỗi/không có lỗi
trong hệthống đang được kiểm tra. Chúng ta cho phép các chuyên gia kiểm thử
tập trung thời gian và tài nguyên của họvào các khu vực có vấn đềcủa hệthống
đang phát triển bằng cách sửdụng dựđoán lỗi phần mềm. Chúng ta có thểtận
dụng các phương pháp dựđoán lỗi và hướng nỗlực và nguồn lực của mình đến
những nơi mà chúng ta dựđoán có lỗi. Một lợi ích khác của SFP là nhận thức về
phân bốlỗi trước khi tiến hành kiểm tra, khi chúng ta sửdụng dữliệu trước đó
đểcải thiện chất lượng của các bản phát hành tiếp theo vì chúng ta có ý tưởng về
sựhiện diện của lỗi trong một phần cụthểcủa hệthống kiểm thửtrước khi bắt
đầu kiểm tra.
Mục tiêu của các mô hình dựđoán lỗi phần mềm là xác định các mô-đun dễbị
lỗi (ví dụ: tập tin, lớp, gói và chức năng) trong hệthống phần mềm nhất định [70].
1


---

Những mô hình dựđoán này giúp người lập trình tập trung vào các mô-đun phần
mềm dễbịlỗi và phân bổnguồn lực của họmột cách tối ưu nhất [40]. Kỹthuật
học máy chủyếu đã được áp dụng trong nhiều năm đểphát triển các mô hình dự
đoán lỗi phần mềm. Các kỹthuật này sửdụng dữliệu lỗi lịch sửcủa phần mềm
(thu được từcác dựán phần mềm trước đó) đểhuấn luyện các mô hình dựđoán
và dựđoán các mô-đun bịlỗi [69, 53]. Dữliệu lỗi lịch sửchứa các giá trịcủa các
độđo phần mềm khác nhau ( ví dụ: coupling between objects, lines of code) và
các nhãn (lỗi - không lỗi) cho mỗi mô-đun trong tập dữliệu. Trong quá trình huấn
luyện, mô hình dựđoán thu được kiến thức vềđặc điểm của dựán phần mềm và
sửdụng kiến thức này đểdựđoán xem mô-đun khác có bịlỗi hay không [32].
Các mô hình SFP bịảnh hưởng bởi một loạt các yếu tố. Những yếu tốnày bao
gồm vấn đềoverfitting của mô hình, nhiễu trong tập dữliệu, các tham sốchi phí,
các độphần mềm, lựa chọn đặc trưng, v.v. Một trong những vấn đềnghiêm trọng
nhất với các tập dữliệu lỗi là vấn đềmất cân bằng dữliệu. Một tập dữliệu thiên
lệch với sựphân bốkhông đều của các lớp được gọi là tập dữliệu mất cân bằng.
Một lớp dữliệu chiếm đa số, trong khi lớp dữliệu khác chiếm thiểu số. Khi một
mô hình được áp dụng cho tập dữliệu này, nó tạo ra kết quảthiên lệch, dẫn đến
đánh giá hệthống không chính xác. Đểgiải quyết vấn đềnày, các thuật toán lấy
mẫu khác nhau được sửdụng. Những thuật toán lấy mẫu này được kết hợp với
các thuật toán học mẫu đểtạo ra các mô hình SFP hiệu suất cao.
Tuy nhiên, hầu hết các bộdữliệu lỗi lịch sửbao gồm nhiều mô-đun không bị
lỗi (tức là lớp đa số) hơn các mô-đun bịlỗi (tức là lớp thiểu số). Đây được gọi là
vấn đềmất cân bằng lớp trong dựđoán lỗi phần mềm. Nhiều kỹthuật học máy giả
định rằng tÿ lệmô-đun lớp thiểu sốvà mô-đun lớp đa sốlà xấp xß bằng nhau [4].
Do đó, các mô hình dựđoán được xây dựng trên bộdữliệu phần mềm không cân
bằng có khảnăng không học được các mẫu mô-đun bịlỗi và do đó có xu hướng dự
đoán không chính xác nhiều mô-đun bịlỗi [44]. Điều này có thểdẫn đến các mô
hình dựđoán không đáng tin cậy và không thểsửdụng trong thực tế. Do đó, việc
đềxuất các kỹthuật/phương pháp đểgiải quyết vấn đềmất cân bằng lớp của bộ
dữliệu lỗi là một vấn đềđược cân nhắc kỹlưỡng trong dựđoán lỗi phần mềm.
2


---

Đểgiải quyết vấn đềnày, các thuật toán lấy mẫu khác nhau được sửdụng.
Những thuật toán lấy mẫu này được kết hợp với các thuật toán học mẫu đểtạo ra
các mô hình SFP hiệu suất cao. Các kỹthuật lấy mẫu dữliệu như oversampling
và under-sampling được sửdụng rộng rãi đểgiải quyết vấn đềmất cân bằng lớp
trong dựđoán lỗi phần mềm [44, 6]. Kỹthuật oversampling tăng sốlượng mẫu ở
lớp thiểu số. Ngược lại, kỹthuật under-sampling loại bỏmột sốmô-đun lớp đa
sốđểcân bằng tÿ lệmô-đun lớp thiểu sốvà lớp đa số[39]. Cảhai kỹthuật đều
nhằm mục đích cân bằng việc biểu diễn các mô-đun lớp thiểu sốvà lớp đa sốđểcải
thiện hiệu suất của mô hình dựđoán. Trong dựđoán lỗi phần mềm, các kỹthuật
oversampling thường được sửdụng so với các kỹthuật under-sampling, vì kỹthuật
lấy mẫu dưới đây sẽloại bỏcác mô-đun một cách tùy ý khỏi tập dữliệu. Do đó,
một sốthông tin quan trọng có thểbịmất khỏi tập dữliệu. Đểthực hiện kí thuật
oversampling, các kỹthuật như SMOTE và biến thể(ví dụ: ADASYN, Border-line
SMOTE) và lấy mẫu (Random Oversampling (ROS) hầu hết được sửdụng. Kỹ
thuật ROS chß đơn giản sao chép các mô-đun lớp thiểu sốđểcân bằng tập dữliệu
mà không cần thêm bất kỳthông tin mới nào [30]. Điều này dẫn đến một mô hình
dựđoán sẽgặp vấn đềoverfitting - mô hình sẽđúng trên tập huấn luyện nhưng
trên tập test thì cho ra kết quảkhông chính xách, vì vậy có thểkhông hoạt động
chính xác đối với các mô-đun thửnghiệm được. Các kỹthuật dựa trên SMOTE
tạo ra các mô-đun lớp thiểu sốtổng hợp bằng cách nội suy các mô-đun lân cận
đã xác định (dựa trên khoảng cách) đểcân bằng tập dữliệu [41, 14]. Các mô-đun
mới được thêm vào này không trùng lặp như trong ROS, nhưng do các mô-đun
lân cận, các kỹthuật dựa trên SMOTE không tạo ra các mô-đun lớp thiểu sốđa
dạng, điều này có thểdẫn đến việc overfitting trên các mô hình dựđoán (hiệu suất
thấp trên tập hợp con thửnghiệm). Một sốcông trình khác như Feng et al. [56]
và Bennin và Bennin [23, 24], đã đềxuất các kỹthuật lấy mẫu quá mức dựa trên
độphức tạp (complexity-based) và dựa trên tính đa dạng (diversity-based)tương
ứng. Tuy nhiên, những kỹthuật này tạo ra hiệu suất dựđoán lỗi hạn chế. Các
kỹthuật cost-sensitive [22] và các kỹthuật ensemble-based techniques [55] cũng
đã được sửdụng đểhọc vềsựmất cân bằng trong dựđoán lỗi phần mềm. Tuy
3


---

nhiên, Galar [37] đã phát hiện ra rằng các kỹthuật học tập bagging và boosting
sẽcải thiện độchính xác của các mô hình dựđoán lỗi phần mềm nhưng không
được thiết kếđểxửlý các tập dữliệu không cân bằng.
Generative Adversarial Networks (GAN) [2] gần đây đã được áp dụng thành
công đểgiải quyết các vấn đềmất cân bằng dữliệu trong một sốlĩnh vực, chẳng
hạn như tạo hình ảnh và video và xửlý ngôn ngữtựnhiên. GAN chủyếu được
phát triển đểtạo hình ảnh, dạng bảng và các loại dữliệu khác [26, 54]. Các phương
pháp tiếp cận GAN đã được chứng minh là có thểtìm hiểu cách phân phối tốt
hơn các kỹthuật lấy mẫu dữliệu cơ sởvà khắc phục một cách hiệu quảvấn đề
vềcác lớp không cân bằng [54]. Trong nghiên cứu này, chúng tôi tập trung vào
đánh giá thực nghiệm các kỹthuật GAN tiềm năng và các biến thểcủa nó đểtạo
ra bộdữliệu lỗi phần mềm trong bài toán dựđoán lỗi. Ngoài ra, các đặc trưng
không liên quan và dư thừa cũng ảnh hưởng đến tốc độvà độchính xác của các
mô hình học máy được đào tạo [68]. Kỹthuật lựa chọn đặc trưng phần mềm là
cần thiết đểchọn các tập hợp con tốt nhất của độđo phần mềm nhằm đạt được
kết quảdựđoán tốt [10]. Do đó, trong nghiên cứu này, chúng tôi đã áp dụng bốn
kỹthuật lựa chọn đặc trưng đểchọn ra các độđo/đặc trưng phần mềm tối ưu
có hiệu quảđểhuấn luyện các mô hình dựđoán lỗi. Ngoài ra, mục tiêu chính
trong nghiên cứu của chúng tôi là xửlý vấn đềmất cân bằng lớp có thểcải thiện
hiệu suất dựđoán. Đểkhắc phục cảtình trạng mất cân bằng lớp và loại bỏđặc
trưng không liên quan/dư thừa, chúng tôi áp dụng ba mô hình GAN bao gồm
VanillaGAN, CTGAN và WANGGP [54] đểtạo các mẫu tổng hợp nhằm cân bằng
giữa nhóm thiểu sốvà nhóm đa sốtrong bộdữliệu lỗi phần mềm kết hợp bốn kỹ
thuật lựa chọn đặc trưng (Chi-Squared, Information Gain, Fisher và Relief) dựa
trên xếp hạng đểxác định sựkết hợp hoạt động tốt nhất cho các mô hình dựđoán
lỗi. Chúng tôi đã xem xét đánh giá mô hình dựđoán lỗi trên các độđo đánh giá
bao gồm Precision, Recall, F1-score và Area Under the ROC Curve (AUC) đểso
sánh hiệu suất của các kết hợp khác nhau giữa kỹthuật lựa chọn đặc trưng và các
phương pháp xửlý dữliệu mất cân bằng GAN. Đóng góp của báo cáo này như
sau:
4


---

1. Tiến hành thực nghiệm đểkiểm tra cách tiếp cận kết hợp giữa 4 kỹthuật
lựa chọn đặc trưng dựa trên bộlọc và 3 kỹthuật oversampling trên 4 bộdữ
liệu lỗi được trích xuất từkho lưu trữPROMISE [71] sửdụng các thuật toán
phân loại khác nhau như Random Forest (RF), Extra Tree (ET), AdaBoost
(AdaBoost), Histogram-based Gradient Boosting (HGB) đểđưa ra kết luận
vềcác kết hợp tốt nhất.
2. Hiệu suất của các mô hình dựđoán lỗi được so sánh với việc áp dụng các kỹ
thuật lấy mẫu và lựa chọn đặc trưng đểkiểm tra tác động đáng kểcủa các
kỹthuật này trong việc xửlý các đặc trưng không liên quan/dư thừa và giải
quyết hiệu quảvấn đềmất cân bằng lớp.
Phần còn lại của bài báo như sau: Mục 2 cung cấp kiến thức nền tảng vềdự
đoán lỗi phần mềm và các bước liên quan trong quá trình này. Các nghiên cứu liên
quan được trình bày trong mục 3 của báo cáo. Mục 4 trình bày các mô hình GAN
cho việc lấy mẫu dữliệu trong dựđoán lỗi phần mềm. Xây dựng thực nghiệm và
kết quảthực nghiệm được trình bày trong mục 5. Mục 6 sẽtrình bày các kết luận
của báo cáo.
2
Dựđoán lỗi phần mềm
2.1
Tổng quan vềdựđoán lỗi phần mềm
Dựđoán lỗi phần mềm là kỹthuật dựđoán các đoạn phần mềm có lỗi trước giai
đoạn kiểm thửtrong quá trình phát triển phần mềm. Điều này tạo điều kiện sử
dụng tài nguyên hiệu quảvà hoàn thành phát triển phần mềm đúng hạn. Đểxây
dựng các mô hình dựđoán lỗi, các thuật toán học máy khác nhau được áp dụng.
Các mô hình ensemble models là những mô hình được áp dụng nhiều nhất gần đây
cho dựđoán lỗi. Hiệu suất của quá trình SFP bịảnh hưởng bởi nhiều yếu tố. Tất
cảnhững yếu tốnày đóng vai trò quan trọng trong việc xây dựng một mô hình có
cấu trúc và chính xác. Một sốyếu tốbao gồm:
1. Độđo phần mềm
5


---

2. Tập dữliệu
3. Các kỹthuật học máy
4. Lựa chọn các đặc trưng phần mềm
5. Độđo đánh giá
6. Các vấn đềvềtập dữliệu
Trong khi phát triển một mô hình đểphát hiện lỗi trong một mô-đun phần mềm,
các nhà phát triển phải đối mặt với nhiều thách thức. Những yếu tốnày có thể
ảnh hưởng đến hiệu quảvà độchính xác của mô hình. Các nhà phát triển cần chú
ý đến tất cảnhững yếu tốnày khi phát triển một công cụ. Một sốyếu tốbao gồm:
1. Mất cân bằng tập dữliệu
2. Tập dữliệu bịnhiễu
3. Vấn đềcác mô hình huấn luyện bịoverfitting
4. Các tham sốmô hình
Kỹthuật lấy mẫu quá mức (oversampling) và lấy mẫu thiếu (under-sampling)
thường được sửdụng đểcân bằng dữliệu nhằm giải quyết các vấn đềmất cân
bằng lớp. Trong báo cáo này, chúng tôi tập trung đến vấn đềmất cân bằng dữliệu
và các kỹthuật lấy mẫu liên quan.
2.2
Quy trình dựđoán lỗi phần mềm
Dựđoán lỗi phần mềm là một phương pháp dựđoán các mô-đun dễbịlỗi của các
dựán phần mềm trước giai đoạn thửnghiệm. Dựđoán lỗi phần mềm tạo điều kiện
thuận lợi cho việc chẩn đoán sớm và xác định các thành phần có thểchứa lỗi và
do đó giúp các nhà phát triển phần mềm phát hiện hầu hết các lỗi xảy ra trong
bản phát hành phần mềm hiện tại. Mô hình dựđoán lỗi phần mềm được đào tạo
dựa trên dữliệu lỗi lịch sửbằng cách sửdụng mô hình học máy từcác phiên bản
phần mềm trước đó. Sau đó, mô hình được đào tạo sẽđược áp dụng đểdựđoán
6


---

lỗi của các mô-đun trong phiên bản hiện tại của dựán. Như được minh họa trong
Hình. 1, quy trình dựđoán lỗi phần mềm bao gồm các bước sau:
Hình 1: Quy trình dựđoán lỗi phần mềm.
1. Thu thập dữliệu: Thu thập tập dữliệu lỗi được tạo hoặc có sẵn công khai
từnhiều kho phần mềm khác nhau như PROMISE, NASA và Apache.
2. Tiền xửlý dữliệu: Tập dữliệu lỗi phần mềm có thểchứa nhiễu, dữliệu
nhiều chiều, sựhiện diện của các thuộc tính không liên quan hoặc dư thừa,
các ngoại lệvà các lớp không cân bằng. Do đó, các kỹthuật tiền xửlý dữ
liệu khác nhau được áp dụng, chẳng hạn như chuẩn hóa dữliệu, lựa chọn đặc
trưng, trích xuất đặc trưng và lấy mẫu dữliệu, đểcải thiện hiệu suất của các
mô hình dựđoán lỗi.
3. Trích xuất các đặc trưng và xây dựng tập dữliệu đào tạo: Ởbước
này, các độđo phần mềm được trích xuất từmã nguồn hoặc nhật ký lịch sử
của các dựán phần mềm. Các độđo phần mềm được trích xuất được kết hợp
với thông tin lỗi đểtạo tập dữliệu huấn luyện được sửdụng làm đầu vào cho
mô hình học máy đểdựđoán lỗi.
4. Xây dựng mô hình dựđoán lỗi: Các kỹthuật thống kê, mô hình học máy
hoặc mô hình học sâu được khai thác đểxây dựng mô hình dựđoán bằng
7


---

cách sửdụng tập dữliệu huấn luyện. Mô hình được đào tạo sau đó được áp
dụng đểdựđoán lỗi trong các mô-đun dễbịlỗi phần mềm.
5. Đánh giá mô hình: Sau các bước huấn luyện, tập dữliệu thửnghiệm được
sửdụng đểkiểm tra mô hình dựđoán lỗi. Hiệu suất của mô hình có thểđược
đo bằng cách so sánh giá trịdựđoán của các mô-đun dễbịlỗi do mô hình
tạo ra với giá trịthực tếcủa các mô-đun dễbịlỗi bằng cách sửdụng các biện
pháp đánh giá như accuracy, precision, recall, the F1-score and AUC.
6. Parameter Tuning: Các hyperparameters của mô hình được điều chßnh để
đạt được độchính xác cao và hiệu suất tốt hơn.
7. Dựđoán lỗi: Mô hình dựđoán lỗi được áp dụng đểxác định các module
phần mềm dễbịlỗi trong các dựán thực tế.
2.3
Độđo phần mềm
Đểnắm bắt được các khía cạnh khác nhau của sản phẩm phần mềm, các nghiên
cứu gần đây đã khai thác các độđo đểdựđoán lỗi phần mềm. Các thước đo chất
lượng khác nhau được sửdụng đểđo lường các đặc tính chất lượng của phần mềm
trong công nghệphần mềm. Chúng được phân loại thành bốn loại [52]: procedural
metrics - độđo thủtục, object-oriented metrics - độđo hướng đối tượng, hybrid
metrics - độđo kết hợp và miscellaneous metrics. độđo thủtục bao gồm các độđo
mã tĩnh ban đầu được trình bày bởi Halsted [33], McCabe [59] và độđo LOC. Độ
đo v(g) của McCabe đo lường độphức tạp của mô-đun phần mềm. độđo hướng
đối tượng, ban đầu được phát triển bởi Chidamber và Kemerer [51] và Lorenz và
Kidd [31], đo lường các đặc điểm của hệthống hướng đối tượng chẳng hạn như
object classes, inheritance and cohesion. độđo kết hợp bao gồm các độđo hướng
đối tượng và thủtục trong dựđoán lỗi phần mềm. Các độđo khác bao gồm các
độđo quy trình, độđo thay đổi và độđo churn. Một sốnhà nghiên cứu đã đềxuất
các mô hình dựđoán sửdụng cảđộđo phần mềm và một sốkỹthuật học máy.
Theo Zimmermann et al [61], các độđo phức tạp có thểđược tổng hợp đểdựđoán
lỗi. Họđã phát hành tập dữliệu Eclipse, được tạo bằng cách ánh xạcác lỗi từcơ
8


---

sởdữliệu lỗi tới vịtrí của chúng trong mã nguồn và sau đó công khai tất cảdữ
liệu trên Kho lưu trữmáy học của UCI. Cata và Diri [5] đã xem xét các tài liệu kÿ
yếu hội nghịvà tạp chí được xuất bản trong lĩnh vực dựđoán lỗi phần mềm với
nhiều loại tập dữliệu, độđo và phương pháp khác nhau. Họkết luận rằng, mặc
dù các độđo ởcấp độphương pháp được sửdụng rộng rãi trong nghiên cứu dự
đoán lỗi trước đây, nhưng tÿ lệsửdụng các độđo ởcấp độlớp, cấp thành phần
và cấp quy trình vẫn vượt quá mức chấp nhận được của các mô hình dựđoán.
Ruchika và Malhotra [49] đã tiến hành đánh giá có hệthống vềnhiều loại độ
đo phần mềm, kỹthuật máy học và bộdữliệu. Họkết luận rằng các thước đo
hướng đối tượng là thước đo hiệu quảnhất đểdựđoán lỗi phần mềm do mức độ
lỗi thiết kếtrong phần mềm cao. Cụthể, LOC (dòng mã), CBO (khớp nối giữa các
đối tượng) và RFC (phản hồi cho một lớp) là các độđo hiệu quảcho các kỹthuật
lựa chọn đặc trưng. Ngược lại, độđo DIT (độsâu của cây kếthừa) và NOC (số
lượng con) được đềcập là không hữu ích trong dựđoán lỗi phần mềm. Meiliana và
Karim [34] đã tiến hành đánh giá tài liệu vềmột sốđộđo phần mềm đểdựđoán
lỗi phần mềm bằng kỹthuật máy học. Dựa trên quan sát của họtừnhiều tài liệu
nghiên cứu khác nhau, các độđo cấp độlớp đã được chứng minh là hiệu quảhơn
các độđo cấp phương pháp trong việc dựđoán lỗi. Nam và Kim [19] đã trình bày
hai phương pháp dựđoán lỗi là CLA và CLAMI, sửdụng độlớn của giá trịđộ
đo đểgắn nhãn cho tập dữliệu không được gắn nhãn. Họkết luận rằng phương
pháp của họđạt được hiệu suất tốt hơn so với các mô hình dựđoán điển hình và
có ứng dụng tiềm năng đểdựđoán lỗi đối với các dựán có bộdữliệu không được
gắn nhãn. Yang et al. [66] đã đềxuất một mô hình không giám sát bằng cách sử
dụng các độđo thay đổi đểdựđoán lỗi đúng lúc, nhận thức được nỗlực. Nam et
al. [20] đã đềxuất một kỹthuật dựđoán lỗi không đồng nhất bằng cách sửdụng
các bộđộđo không đồng nhất đểdựđoán lỗi trong dựđoán lỗi liên dựán. Cách
tiếp cận của họmang lại kết quảđầy hứa hẹn và chứng tỏmức độkhảthi cao.
9


---

2.4
Lựa chọn đặc trưng
Các thuật toán học máy thường được sửdụng cho nhiều ứng dụng khác nhau,
bao gồm nhận dạng mẫu, khai thác dữliệu và mô hình dựđoán. Các thuật toán
này có khảnăng học hỏi mạnh mẽtừcác không gian đặc trưng có nhiều chiều và
nhiều thông tin. Tuy nhiên, không gian đặc trưng nhiều chiều có thểdẫn đến hiện
tượng khớp quá mức, tăng độphức tạp tính toán và giảm khảnăng diễn giải mô
hình. Lựa chọn đặc trưng [16] là một bước tiền xửlý quan trọng nhằm mục đích
giảm kích thước của tập dữliệu bằng cách chọn một tập hợp con các đặc trưng
có liên quan từmột nhóm lớn các thuộc tính ứng cửviên. Phần này cung cấp cái
nhìn tổng quan toàn diện vềcác kỹthuật lựa chọn đặc trưng, bao gồm các phương
thức filter, wrapper và embedded.
2.4.1
Lựa chọn đặc trưng dựa trên Filter
Các phương pháp lựa chọn đặc trưng dựa trên filter [42] dựa trên các đặc điểm xếp
hạng bằng cách sửdụng các phép đo thống kê, chẳng hạn như mutual information,
chi-squared, or correlation coefficients. Các phương thức này độc lập với mô hình
phân lớp được sửdụng và các đặc trưng được chọn sẽđược sửdụng làm đầu vào
cho mô hình phân lớp. Các phương pháp filter có hiệu quảvềmặt tính toán vì
chúng không yêu cầu đào tạo mô hình học máy cho từng tập hợp con đối tượng.
Một trong những phép đo thống kê thường được sửdụng trong các phương
pháp lọc là thông tin lẫn nhau [10], đo lường sựphụthuộc giữa hai biến. Thông
tin tương hỗgiữa một đối tượng
MI(x, y) = Σc
i=1Σd
j=1(p(xi, yj)log(p(xi, yj)/p(xi)p(yj)))
(1)
trong đó c và d lần lượt là sốgiá trịduy nhất của x và y, và p(xi) và p(yj) là giá
trịcận biên xác suất của xi và yj tương ứng. Giá trịthông tin lẫn nhau cao cho
thấy mối quan hệchặt chẽgiữa đối tượng địa lý và biến mục tiêu, làm cho các đặc
điểm này phù hợp hơn đểsửdụng trong vectơ đầu vào.
10


---

2.4.2
Lựa chọn đặc trưng dựa trên Wrapper
Các kỹthuật lựa chọn đặc trưng dựa trên wrapper [47] xem xét sựtương tác giữa
một tập hợp các đặc trưng và một mô hình phân loại. Ý tưởng cơ bản là đánh giá
hiệu suất của mô hình phân loại trên các tập hợp con đối tượng khác nhau, chọn
tập hợp con mang lại hiệu suất tốt nhất. Quá trình tìm kiếm có thểđược thực
hiện bằng cách sửdụng tìm kiếm toàn diện, tìm kiếm tham lam hoặc tìm kiếm
ngẫu nhiên. Một cách tiếp cận phổbiến là sửdụng thuật toán tìm kiếm tham lam,
chẳng hạn như backward elimination, trong đó các thuộc tính được loại bỏtừng
đặc trưng một cho đến khi đạt được hiệu suất thỏa đáng.
Phương thức lựa chọn đặc trưng dựa trên wrapper có thểđược xây dựng dưới
dạng một bài toán tối ưu hóa, trong đó mục tiêu là tìm ra tập hợp con đặc trưng
tốt nhất giúp tối đa hóa hiệu suất của bộphân loại. Đặt F là tập hợp tất cảcác
đặc trưng, S là tập con của F, và J(S) là hiệu suất của bộphân loại trên tập con
đặc trưng S. Phương pháp lựa chọn đặc trưng dựa trên wrapper có thểđược xây
dựng như sau:
S∗= argmaxS(J(S))
(2)
where S∗là tập đặc trưng dữliệu tối ưu thu được.
2.4.3
Lựa chọn đặc trưng dựa trên Embedded
Các kỹthuật lựa chọn đặc trưng dựa trên Embedded [3] là sựkết hợp giữa các
phương thức filter và wrapper, trong đó việc lựa chọn đặc trưng được tích hợp
vào thuật toán học tập được mô hình phân lớp sửdụng. Các phương pháp này
hiệu quảhơn vềmặt tính toán so với các phương pháp bao bọc, vì quá trình
lựa chọn đặc trưng được thực hiện như một phần của quá trình đào tạo. Các
phương pháp Regularization, chẳng hạn như Lasso (Least Absolute Shrinkage and
Selection Operator) và Ridge Regression, là những ví dụphổbiến của các kỹthuật
lựa chọn đặc trưng dựa trên Embedded. Các phương pháp này sửdụng sốhạng
phạt đểthu nhỏhệsốcủa các đặc tính ít quan trọng hơn về0, loại bỏchúng khỏi
mô hình một cách hiệu quả. Lasso [45], Hồi quy Ridge [11] và ElasticNet [11] là
11


---

các kỹthuật chính quy hóa được sửdụng trong hồi quy tuyến tính đểngăn chặn
quá mức và cải thiện độchính xác dựđoán của mô hình.
2.5
Các mô hình học máy
Một sốnghiên cứu [63, 35, 13] đã chứng minh rằng máy học (Machine Learning)
có thểđược áp dụng thành công đểxây dựng các mô hình dựđoán lỗi phần mềm
nhằm phân loại các nhãn Dễxảy ra lỗi (Fault Prone) và Không dễxảy ra lỗi (None-
Fault-Prone ). Nhiều nhà nghiên cứu đã phát hiện ra rằng hiệu suất của các mô
hình dựđoán có sựkhác biệt đáng kểđối với các mô hình phân loại khác nhau [25].
Các nghiên cứu của Malhotra [49] và Wang [9] đã được xem xét đểlựa chọn các
cấu hình và kỹthuật máy học dùng trong nghiên cứu này. Trong sốcác kỹthuật
khác nhau được trình bày trong miền dựđoán lỗi phần mềm như học tập tổng
hợp, mạng nơ-ron nhân tạo và mô hình học sâu, chúng tôi đã xem xét các kỹthuật
sau: Random Forest [12], Extreme Gradient Boosting (XGBoost) [62], Histogram-
based Gradient Boosting (HGBoost) [1], Multilayer Perceptron (MLP) [57], Extra
Trees [43] và Adaptive Boosting (AdaBoost) [67].
Tumar et al. [18] đã đềxuất một mô hình SFP dựa trên tối ưu hóa Binary Moth
Flame kết hợp với phương pháp lấy mẫu tổng hợp thích ứng (Adaptive Synthetic
Sampling - ADASYN) đểgiải quyết vấn đềmất cân bằng dữliệu. Khi áp dụng
vào tập dữliệu PROMISE, kỹthuật được đềxuất này cải thiện hiệu suất của các
bộphân loại khác nhau. Trong sốđó, Phân tích Phân biệt Tuyến tính (Linear
Discriminant Analysis - LDA) có giá trịAUC cao nhất và KNN là tốt nhất vềthời
gian thực thi. Rathore et al. [54] đã giới thiệu ba phương pháp tạo mẫu quá mức
riêng biệt là Conditional GAN (CT-GAN), Vanilla GAN, và Wasserstein GAN với
Gradient Penalty (WGANGP). Thực nghiệm nghiệm được thực hiện trên các tập
dữliệu PROMISE, JIRA và Eclipse. Khi các phương pháp lấy mẫu này được sử
dụng với các mô hình cơ sởtrong các bài kiểm tra trên các tập dữliệu lỗi, kết
quảcủa các mô hình cơ sởđược cải thiện đáng kể. Đối với SFP trong các mô
hình trong phiên bản và giữa các phiên bản, Singh và Rathore [46] đã áp dụng các
phương pháp hồi quy Bayesian phi tuyến tính và tuyến tính. Các phương pháp lấy
12


---

mẫu dữliệu SMOTE được áp dụng cùng với Random Forest (RF), Support Vector
Machine (SVM), Linear Regression (Lr), Linear Bayesian Regression (LBr), and
Non-linear Bayesian Regression (NLBr). Hồi quy Bayesian phi tuyến tính đã vượt
trội hơn các phương pháp hồi quy tuyến tính trên một mẫu chứa 46 dựán phần
mềm khác nhau.
3
Các nghiên cứu liên quan
Dựđoán lỗi phần mềm là lĩnh vực phổbiến nhất trong công nghệphần mềm miền
trong ba thập kÿ qua [49]. Nhiều mô hình máy học đã được áp dụng trước đó cho
các mô hình dựđoán lỗi như Decision tree, Na¨ıve Bayes, Logistic Regression, Sup-
port Vector Machine, Multilayer Perceptron, Random Forest và Ensemble learning.
Những kỹthuật này mang lại hiệu suất đáng kểcho các mô hình dựđoán lỗi phần
mềm. Tuy nhiên, trong bộdữliệu lỗi phần mềm, việc biểu diễn các mô-đun bịlỗi
(lớp thiểu số) ít hơn nhiều so với các mô-đun không bịlỗi (lớp đa số), đây là vấn đề
mất cân bằng lớp. Do vấn đềnày, hiệu suất của các mô hình dựđoán lỗi bịgiảm
nghiêm trọng. Nhiều nghiên cứu đã cốgắng giải quyết vấn đềnày của mô hình
dựđoán lỗi phần mềm [23, 55]. Vềcơ bản, các phương pháp lấy mẫu sampling,
phương pháp ensemble và phương pháp cost-sensitive đã được áp dụng trước đó
đểgiải quyết vấn đề. Các phương pháp lấy mẫu bao gồm kỹthuật under-sampling
và oversampling. Các kỹthuật oversampling như SMOTE và ROS và các kỹthuật
under-sampling như RUS đã được áp dụng rộng rãi cho dựđoán lỗi phần mềm.
Kamei [65] đã đánh giá các phương pháp lấy mẫu khác nhau (ROS, SMOTE, RUS
và one-sided selection) cho dựđoán lỗi bằng các kỹthuật học máy khác nhau trong
công việc của họ. Các tác giảđã chß ra rằng các phương pháp lấy mẫu giúp cải
thiện hiệu suất của các mô hình tuyến tính và mô hình logistic, trong khi mạng
nơ-ron và mô hình cây phân loại lại hoạt động kém hơn. Trong một nghiên cứu
tương tựkhác, Tan [38] đã đánh giá bốn phương pháp lấy mẫu (simple duplicate,
spread subsample, SMOTE, and resampling with/without replacement). Kết quả
thửnghiệm cho thấy phương pháp resampling hoạt động tốt nhất trong sốtất cả
13


---

các phương pháp lấy mẫu tổng thểvà cải thiện hiệu suất dựđoán.
Các phương pháp ensemble learning giải quyết vấn đềmất cân bằng lớp bằng
cách tạo và kết hợp một sốmô hình học máy đểcó được mô hình học máy mạnh.
Các phương pháp tập hợp được sửdụng phổbiến nhất là bagging, boosting, and
stacking. Một sốbiến thểnhư Under-Bagging, OverBagging, UnderOverBagging,
SMOTBagging, RUSBoost và SMOTEBoost đã được áp dụng cho dựđoán lỗi
phần mềm [44], [7]. Siers và Islam [36] đã đềxuất một phương pháp cost-sensitive
và tiếp cận knowledge discovery cho việc học không cân bằng trong dựđoán lỗi
phần mềm. Các tác giảđã xác nhận tính hiệu quảcủa phương pháp được đềxuất
cho bộdữliệu của NASA và kết quảcho thấy phương pháp được trình bày vượt
trội hơn các phương pháp lấy mẫu được so sánh khác. Gần đây, một sốnghiên cứu
như Malhotra và Kamal [48], Song [44], Phong [56], và Gong [29] đã khám phá
việc sửdụng các phương pháp lấy mẫu và các phương pháp khác đểxửlý vấn đề
mất cân bằng lớp trong dựđoán lỗi phần mềm. Các công trình này báo cáo rằng
việc giải quyết vấn đềmất cân bằng lớp trong việc xây dựng mô hình dựđoán lỗi
sẽmang lại hiệu suất được cải thiện tổng thể.
4
Mô hình GAN cho lấy mẫu dữliệu trong dự
đoán lỗi phần mềm
4.1
Mô hình mạng GAN
Mạng GAN được GoodFellow et al. [15] giới thiệu vào năm 2014 và được định
nghĩa là một trò chơi giữa hai mạng nơ-ron nhân tạo thường được gọi là generator
và discriminator. Bộgenerator cốgắng tìm hiểu tÿ lệphân phối của dữliệu thực
và tạo ra các phiên bản mới có thểđánh lừa bộdiscriminator. Mục đích của bộ
discriminator là phân loại các mẫu thực và tạo ra các mẫu chính xác nhất có thể.
Cảbộgenerator và discriminator đều được huấn luyện đồng thời và cũng chạy
cạnh tranh với nhau trong giai đoạn huấn luyện. Mục tiêu của quá trình đào tạo
GAN là tìm ra điểm cân bằng Nash [28], đây là trạng thái mà cảhai mạng đều có
14


---

thểđạt được hiệu suất tối ưu. Trạng thái cân bằng Nash trong GAN đạt được khi
bộgenerator tạo ra dữliệu tổng hợp không thểphân biệt được với dữliệu thực và
bộdiscriminator không thểcải thiện khảnăng phân biệt giữa mẫu thực và mẫu
được tạo. Tại thời điểm này, GAN đã nắm bắt được sựphân bốcủa dữliệu thực
và có thểtạo ra các mẫu dữliệu mới tương tựvới dữliệu thực. Do ứng dụng thành
công của GAN cho nhiều ứng dụng nghiên cứu và đã được khai thác đểáp dụng
trong nhiều lĩnh vực như xửlý ngôn ngữtựnhiên, thịgiác máy tính và mô hình
phân loại. Van Sloun et al. [50] đã khai thác GAN đểtạo ra hình ảnh có độphân
giải cao từhình ảnh siêu âm thu được bằng cách tích hợp nhiều mô hình học sâu
khác nhau. Fathi-Kazerooni [58] giới thiệu GAN Tunnel đểphát hiện và xác định
tình hình giao thông nhằm cải thiện chức năng điều khiển tựlái của ô tô.
4.2
VanillaGAN
Vanilla GAN [15] là phiên bản được xuất bản sớm nhất của Mạng GAN. Kiến
trúc mô hình GAN bao gồm hai mô hình con: mô hình generator và mô hình
discriminator. Với một sốbiến nhiễu z làm đầu vào, bộG sẽtạo ra các mẫu gần
với dữliệu mục tiêu thực hơn. Mô hình phân biệt D cốgắng phân biệt xem các
mẫu đầu vào đến từbộtạo G hay từdữliệu thực. Đối tượng min-max có thểđược
hình thức hóa như sau:
min(G)max(D)(Ex∼pD[log(D(x))] + Ez∼pz[log(1 −D(G(z)))])
(3)
trong đó, x là dữliệu đầu vào, pD và pz lần lượt thểhiện sựphân bốcủa dữliệu
thực và dữliệu được sinh ra, z ∼pz là nhiễu lấy mẫu từphân phối Gauss or phân
phối đồng nhất. Mục tiêu này dựa trên hàm loss Binary-Cross Entropy (BCE).
Đầu ra của Discriminator D nằm trong phạm vi [0,1] bằng cách sửdụng hàm kích
hoạt sigmoid. Đểtìm hiểu các tham sốcủa GAN, bộphân biệt D cần được đào
tạo cho đến khi đạt được độchính xác tối đa đểphân biệt dữliệu đầu vào với dữ
liệu được tạo G(z) hoặc dữliệu thực. Bộgenerator được huấn luyện đểđạt được
mức tối thiểu log(1 −D(G(z)). Quá trình huấn luyện được thực hiện luân phiên
15


---

cho đến khi đạt được giải pháp chung trong trường hợp pdata = pg.
4.3
Conditional GAN - CTGAN
CTGAN [27] là một biến thểcủa GAN đểlập mô hình phân phối dữliệu dạng
bảng. Đểxửlý các cột chứa phân phối không phải Gaussian và đa phương thức,
CTGAN thay thếchuẩn hóa tối thiểu - tối đa bằng cách khai thác chuẩn hóa theo
chếđộcụthể. Trong chuẩn hóa theo chếđộcụthể, các giá trịliên tục được chuyển
đổi thành các vectơ giới hạn là đầu vào phù hợp với mạng nơ-ron. CTGAN áp dụng
mô hình Hỗn hợp Gaussian (VGM) có thểthay đổi [8] đểdựbáo sốlượng modes
và điều chßnh Gaussian Mixture cho mỗi cột giá trịliên tục. Gaussian Mixture đã
học được định nghĩa như sau:
Pci(ci,j) =
l
X
k=1
µkN(ci,j; ηk, Øk)
(4)
trong đó µk là trọng sốvà Øk là độlệch chuẩn của một chếđộ, trong đó xác
suất ρk của ci,j được tính toán cho từng mode. Việc tính toán mật độxác suất
được định nghĩa như sau:
ρk = µkN(ci,j; ηk, øk)
(5)
Sau đó, một mode được lấy mẫu từmật độxác suất đã cho và mode lấy mẫu được
sửdụng đểchuẩn hóa giá trị. ci,j được trình bày bằng cách sửdụng một obe-hot
vector βi,j có kích thước bằng sốlượng các mode và giá trịvô hướng αi,j được sử
dụng đểtrình bày giá trịtrong mode. Do đó, một hàng trong tập dữliệu là sựnối
của các cột liên tục và rời rạc:
rj = α1,j · β1,j · ... · αNc,jβNc,j · d1,j · ... · dNd,j
(6)
trong đó di,j là một one-hot vector của các giá trịrời rạc.
Đểgiải quyết vấn đềmất cân bằng dữliệu trong mô hình phân biệt đối xử,
CTGAN triển khai một bộgenerator có điều kiện và huấn luyện theo mẫu. Đặc
biệt, dữliệu được lấy mẫu lại một cách hiệu quảtheo cách tất cảcác loại biến
rời rạc được lấy mẫu trong quá trình huấn luyện và dữliệu thực sẽđược phục hồi
trong giai đoạn thửnghiệm.
16


---

4.4
Wasserstein GAN With Gradient Penalty - WGANGP
WGAN hay Wasserstein Progressive Growing of Generative Adversarial Networks
là một mô hình tổng quát dựa trên mạng GAN, được Karras et al.
[60] giới
thiệu vào năm 2017. Bằng cách áp dụng hàm mục tiêu ổn định hơn , khoảng cách
Wasserstein, làm nền tảng cho việc huấn luyện, mô hình này nhằm khắc phục
những khó khăn vềtính không ổn định và sụp đổchếđộvốn có trong các GAN
thông thường. Tuy nhiên, trong công thức WGAN ban đầu, độdốc của hàm mất
mát phê bình có thểgặp phải vấn đềvanishing gradient (mất mát đạo hàm, đạo
hàm quá nhỏ, gần như bằng 0), trong đó độdốc trởgradient nên rất nhỏvà gây
ra sựhội tụchậm hoặc thậm chí dừng quá trình huấn luyện. Do đó, bắt đầu với
độphân giải thấp và dần dần mởrộng kích thước đầu vào của mạng generator,
mô hình WANGGP được huấn luyện bằng cách tăng dần độphân giải của hình
ảnh được tạo ra.
Kiến trúc WANGGP có thểđược biểu diễn vềmặt toán học dưới dạng trò chơi
minimax hai người chơi giữa mạng Discriminator D và mạng Generator G, với
mục tiêu là xác định Điểm cân bằng Nash giữa hai mạng. Sau đây là biểu thức
của hàm mục tiêu đểhuấn luyện mô hình WANGGP:
min
G max
D (Ex∼pD[D(x)] −Ez∼pz[D(G(z))]) −λEbx∼pbx

(|| ▽bx D(bx)||2 −1)2
(7)
trong đó x là mẫu từphân phối dữliệu thực pdata(x), z là vectơ nhiễu ngẫu nhiên,
G là mạng Generator, D là mạng Discriminator và λ là hệsốhệsốphạt (penalty
coefficient) [17].
5
Thực nghiệm đềxuất
Như đã đềcập trong phần giới thiệu, dựđoán lỗi phần mềm là một quy trình
quan trọng trong công nghệphần mềm và cũng phụthuộc vào các bộdữliệu lịch
sửđã được thu thập từcác dựán phần mềm trước đó. Và quá trình này vẫn còn
hai thách thức lớn bao gồm dữliệu vẫn còn chứa các thuộc tính dư thừa hoặc
không liên quan đến lỗi và các lớp không cân bằng. Vì vậy chúng tôi đềxuất hai
17


---

các phương pháp tiếp cận đểkiểm tra việc xác định các kết hợp giữa các kỹthuật
lựa chọn đặc trưng và lấy mẫu dữliệu nhằm mang lại hiệu quảhay không trong
việc cải thiện hiệu suất và độchính xác của mô hình dựđoán lỗi đã phát triển.
5.1
Thực nghiệm dựa trên kết hợp giữa kỹthuật lựa chọn
đặc trưng dựa trên Filter (Filter-based feature selec-
tion) và các kỹthuật lấy mẫu GAN
Các bước của phương pháp thực nghiệm đềxuất cho việc kết hợp lựa chọn đặc
trưng dựa trên Filter (filter-based feature selection) và các kỹthuật lấy mẫu dữ
liệu GAN được hiển thịtrong Hình 2. Đầu tiên, chúng tôi đã thu thập bốn bộdữ
liệu lỗi là CM1, KC1, KC2 và PC1 từPROMISE kho. Chuẩn hóa dữliệu bằng kỹ
thuật chuẩn hóa z được áp dụng cho giai đoạn tiền xửlý. Các tập dữliệu chuẩn
hóa được chia thành tập huấn luyện và tập kiểm tra. Sau khi áp dụng ba mô
hình lấy mẫu quá mức GAN bao gồm VanillaGAN, CTGAN và WANGGP đểcân
bằng các tập dữliệu huấn luyện, bốn lựa chọn đặc trưng được lựa chọn dựa trên
filtering - xếp hạng, cụthểlà Chi-Squared, Information Gain, Fisher và Relief để
trích xuất log2N đặc trưng (N - tổng sốđộđo phần mềm trong bộdữliệu lỗi
đầy đủ). Các tập dữliệu huấn luyện cân bằng có các đặc trưng tối ưu tiếp theo
sẽđược huấn luyện trên Random Forest (RF), Extra Tree (ET), AdaBoost (AB)
và HistGradientBoosting (HG). Các bộthực nghiệm sau đó được đưa vào các mô
hình dựđoán lỗi đểso sánh hiệu suất của các mô hình này bằng cách sửdụng kết
hợp các kỹthuật chọn đặc trưng và lấy mẫu dữliệu trên các độđo đánh giá bao
gồm Precision, Recall, F1-score and AUC.
5.2
Thực nghiệm dựa trên kết hợp giữa kỹthuật lựa chọn
đặc trưng dựa trên Wrapper (wrapper-based feature
selection) và các kỹthuật lấy mẫu GAN
Phương pháp lựa chọn đặc trưng dựa trên wrapper sửdụng thuật toán học máy
đểđánh giá hiệu suất của một tập hợp con của các đặc trưng. Thuật toán được
18


---

Hình 2: Mô hình kết hợp giữa kỹthuật lựa chọn đặc trưng dựa trên Filter và các
kỹthuật lấy mẫu GAN.
huấn luyện bằng cách sửdụng các tập hợp con đặc trưng khác nhau và tập hợp
con mang lại hiệu suất tốt nhất được chọn. Một thực nghiệm thứ2 được thực
nghiệm đểkiểm tra tính hiệu quảcủa việc kết hợp sáu phương pháp Wrapper
khác nhau cho chọn tập hợp con các đặc trưng tối ưu và VanillaGAN là một biến
thểcủa mạng GAN đểcân bằng tÿ lệmô-đun bịlỗi và không bịlỗi trong bộdữ
liệu lỗi. Cách tiếp cận tổng thểđược thểhiện trong Hình 3. Trong quá trình tiền
xửlý dữliệu giai đoạn này, chúng tôi điền các giá trịcòn thiếu và áp dụng chuẩn
hóa Z đểchuẩn hóa dữliệu. Tiếp theo, sáu phương pháp wrapper khác nhau,
cụthểlà Genetic Algorithm(GA), Particle Swarm Optimization (PSO), Whale
optimization algorithm (WOA), Cuckoo search (CS), Mayfly Algorithm(MA) và
Binary Bat Algorithm (BBA) đểchọn các đặc trưng quan trọng và phù hợp nhất
đểgiảm bớt các thuộc tính dư thừa/ không liên quan đến lỗi. Các bộdữliệu với
đặc trưng tối ưu được sửdụng đểhuấn luyện mạng VanillaGAN đểkhắc phục tình
trạng mất cân bằng dữliệu. Cuối cùng, các tập dữliệu huấn luyện và tập dữliệu
thực nghiệm này được sửdụng đểđào tạo bằng các kỹthuật học máy, bao gồm:
Neighbors (KNN), Random Forest (RF), Decision Tree (DT), Na¨ıve Bayes (NB)
19


---

and Logistic Regression (LR).
Hình 3: Mô hình kết hợp giữa kỹthuật lựa chọn đặc trưng dựa trên Wrapper và
các kỹthuật lấy mẫu GAN.
5.3
Tập dữliệu thực nghiệm
Năm bộdữliệu lỗi khác nhau từkho lưu trữPromise [21] đã được sửdụng trong
nghiên cứu này. Những bộdữliệu này đã được sửdụng rộng rãi trong nhiều nghiên
cứu vềlỗi phần mềm nghiên cứu dựbáo [64]. Như được hiển thịtrong Bảng ??,
các bộdữliệu không cân bằng. Các thuộc tính độc lập là các độđo mã nguồn
như Độphức tạp theo chu kỳcủa McCabe (v(g)), Độsâu của cây kếthừa (dit),
v.v. và các thuộc tính phụthuộc bao gồm lỗi nhãn (1) hoặc không lỗi (0). Bảng
?? tóm tắt chi tiết vềcác bộdữliệu được sửdụng.
Dữliệu
Dựán
Sốmẫu
Độđo
Sốmẫu NP
Sốmẫu
lỗi
Tÿ lệmất
cân bằng
Sốmẫu
cân bằng
PROMISE
CM1
498
21
449
49
9.84
628
KC1
2109
21
1693
326
15.45
2856
KC2
522
21
415
107
20.49
590
PC1
1109
21
1032
77
6.9
1422
JM1
10885
21
8779
2016
18.5
12288
20


---

Bảng 1: Kết quảmô hình dựđoán lỗi phần mềm không áp dụng kỹthuật lấy mẫu
và lựa chọn đặc trưng
Dataset
Performance Measures
RF
ET
AB
HGB
CM1
Precision
0.511
0.580
0.589
0.577
Recall
0.502
0.556
0.561
0.542
F1-score
0.502
0.563
0.567
0.546
AUC
0.634
0.623
0.703
0.718
KC1
Precision
0.719
0.707
0.689
0.714
Recall
0.579
0.623
0.609
0.640
F1-score
0.596
0.645
0.630
0.663
AUC
0.702
0.710
0.723
0.728
KC2
Precision
0.726
0.694
0.702
0.725
Recall
0.665
0.646
0.671
0.678
F1-score
0.684
0.660
0.683
0.695
AUC
0.701
0.724
0.707
0.721
PC1
Precision
0.763
0.730
0.653
0.714
Recall
0.594
0.593
0.616
0.620
F1-score
0.629
0.624
0.629
0.649
AUC
0.726
0.788
0.746
0.766
Average
Precision
0.679
0.677
0.658
0.682
Recall
0.585
0.605
0.614
0.620
F1-score
0.603
0.623
0.627
0.638
AUC
0.690
0.711
0.719
0.733
5.4
Độđo đánh giá
Đểđánh giá mô hình dựđoán lỗi phần mềm, các độđo đánh giá bao gồm false
positive rate, độchính xác (accuracy), precision, recall, balance and F-measure
được áp dụng. Trước đó, các ký hiệu A, B, C, D được sửdụng trong đó:
21


---

Bảng 2: Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Chi-Squared
and GAN.
Dataset
Performance
Evaluation
Chi-Squared
VanillaGAN
CTGAN
WGANGP
RF
ET
AB
HGB
RF
ET
AB
HGB
RF
ET
AB
HGB
CM1
Precision
0.826
0.856
0.843
0.849
0.843
0.856
0.854
0.837
0.834
0.819
0.828
0.821
Recall
0.712
0.824
0.780
0.810
0.860
0.878
0.848
0.846
0.804
0.832
0.726
0.816
F1-score
0.758
0.834
0.806
0.827
0.849
0.861
0.849
0.840
0.816
0.824
0.766
0.817
AUC
0.635
0.739
0.679
0.706
0.675
0.739
0.723
0.690
0.643
0.657
0.574
0.679
KC1
Precision
0.809
0.816
0.807
0.823
0.817
0.827
0.813
0.825
0.804
0.804
0.797
0.808
Recall
0.759
0.826
0.802
0.831
0.845
0.848
0.841
0.850
0.814
0.808
0.815
0.802
F1-score
0.778
0.820
0.804
0.826
0.820
0.830
0.817
0.830
0.803
0.802
0.801
0.799
AUC
0.752
0.794
0.753
0.780
0.793
0.793
0.745
0.781
0.755
0.734
0.647
0.734
KC2
Precision
0.815
0.785
0.795
0.788
0.798
0.785
0.786
0.787
0.809
0.813
0.807
0.825
Recall
0.809
0.798
0.798
0.796
0.815
0.806
0.8
0.806
0.638
0.672
0.657
0.668
F1-score
0.811
0.788
0.794
0.788
0.792
0.788
0.788
0.791
0.665
0.698
0.682
0.693
AUC
0.777
0.783
0.701
0.773
0.785
0.775
0.658
0.762
0.753
0.799
0.744
0.761
PC1
Precision
0.899
0.919
0.919
0.916
0.877
0.925
0.913
0.930
0.884
0.911
0.887
0.891
Recall
0.824
0.916
0.907
0.916
0.922
0.935
0.921
0.938
0.817
0.814
0.682
0.823
F1-score
0.854
0.917
0.911
0.915
0.897
0.925
0.916
0.929
0.837
0.836
0.739
0.844
AUC
0.780
0.784
0.839
0.826
0.724
0.775
0.838
0.802
0.681
0.698
0.616
0.663
Average
Precision
0.837
0.844
0.841
0.844
0.833
0.848
0.841
0.845
0.833
0.837
0.830
0.836
Recall
0.776
0.841
0.822
0.838
0.860
0.867
0.852
0.860
0.768
0.781
0.720
0.777
F1-score
0.800
0.840
0.829
0.839
0.839
0.851
0.842
0.847
0.780
0.790
0.747
0.788
AUC
0.736
0.775
0.743
0.771
0.744
0.771
0.741
0.759
0.708
0.722
0.645
0.709
1. A là sốlượng mô-đun bịlỗi được dựđoán là lỗi.
2. B là sốmô-đun bịlỗi được phân loại là không có lỗi.
3. C là sốmô-đun không có lỗi được dựđoán là lỗi.
4. D là sốmô-đun không có lỗi được dựđoán là không có lỗi.
1. Độchính xác (accuracy): Tÿ lệlà sốlượng mô đun được dựđoán chính xác
trên tổng sốmô-đun.
accuracy = (A + D)/(A + B + C + D)
(8)
22


---

Từphương trình trên có thểthấy độchính xác bịảnh hưởng bởi tÿ lệcân
bằng của lớp. Tuy nhiên, các bộdữliệu phần mềm thường thì nhiều mô-đun
không có lỗi nhiều hơn các mô-đun bịlỗi. Nếu một mô hình dựđoán tất cả
các mô-đun không bịlỗi, độchính xác sẽrất cao mặc dù không có mô-đun
bịlỗi nào được dựđoán chính xác. Ví dụ, tÿ lệlỗi trung bình của bộdữliệu
PROMISE là 18%. Nếu một mô hình dựđoán tuyên bốtất cảcác mô-đun là
không có lỗi, độchính xác của nó sẽlà 82% mà không dựđoán chính xác bất
kỳmô-đun bịlỗi nào. Do sựmất cân đối giữa các lớp trong tập dữliệu, độ
chính xác không thểđược coi là thước đo thích hợp đểso sánh các mô hình
dựbáo.
2. False positive rate: tß lệbáo động nhầm cũng được biết là xác suất báo động
nhầm. Tÿ lệnày là sốmô-đun không có lỗi được dựđoán sai như sốlỗi của
các mô-đun không có lỗi.
pf = C/(C + D)
(9)
3. Recall: Recall còn được gọi là dựbáo đúng hoặc xác suất phát hiện (probability
of detection). Recall được tính bằng tÿ lệlà sốlượng mô-đun bịlỗi được dự
đoán chính xác là bịlỗi với sốlượng mô-đun bịlỗi.
recall = pd = A/(A + B)
(10)
4. Precision: Tÿ lệlà sốlượng mô-đun bịlỗi được dựđoán chính xác là bịlỗi với
sốlượng mô-đun được dựđoán là lỗi.
precision = A/(A + C)
(11)
Một mô hình dựđoán trình bày một hiệu suất tốt nếu đạt được các giá trịthu
hồi (recall), độchính xác (accuracy) và giá trịthấp hơn của độbáo động giả
(False positive rate). Tuy nhiên, người ta biết rằng việc recall có thểđược cải
thiện bằng cách giảm accuracy và ngược lại. Bởi vì sựcân bằng giữa accuracy
và recall, không dễso sánh các hiệu năng của bộdựđoán lỗi dựa trên chß
recall hoặc accuracy. Kết quảlà, F- measure, một thước đo tổng hợp recall và
accuracy, đã được sửdụng đểso sánh kết quảdựđoán.
23


---

5. F- measure: Chức năng hài hòa của recall và accuracy
F −measure = (2 ∗recall ∗precision)/(recall + precision)
(12)
F-measure đã được sửdụng trong nhiều bài báo dựđoán lỗi. Độđo này trình
bày một điểm thống nhất đểđánh giá mô hình dựđoán sau khi cân bằng sự
cân bằng giữa recall và accuracy. Giá trịcủa F-measure tÿ lệthuận với hiệu
suất của một mô hình.
6. AUC: AUC biểu thịkhu vực theo đường cong (ROC). AUC là một thước đo
không tham sốđộc lập với ngưỡng và không bịảnh hưởng bởi sựmất cân bằng
trong lớp. ROC là một đường cong hai chiều được vẽtheo xác suất của báo
động giả(trục x) và xác suất phát hiện (trục y). Theo Rahman và Devanbu
một mô hình tốt hơn khi đường cong ROC của nó gần với điểm pd = 1 và pf
= 0. Một bộdựbáo hoàn hảo, có AUC là 1. Ngược lại, một đường cong phủ
định minh họa mô hình không tốt với xác suất báo động giảvà xác suất phát
hiện thấp.
5.5
Kết quảthực nghiệm
Trong nghiên cứu này, chúng tôi đã xây dựng các mô hình dựđoán lỗi bằng cách
kết hợp các biến thểGAN khác nhau đểtổng hợp các mẫu mới, sau đó sửdụng
lựa chọn đặc trưng dựa trên filter/ wrapper đểgiảm các thuộc tính không liên
quan hoặc dư thừa. Sau đó, chúng tôi sửdụng các mô hình học máy phổbiến
và đánh giá tác động của sựmất cân bằng lớp và các thuộc tính dư thừa đối với
hiệu suất của các mô hình này. Các thực nghiệm được thực hiện sửdụng 10-fold
cross-validation cho mỗi thửnghiệm. Hiệu suất của các mô hình dựđoán lỗi đã
phát triển được đánh giá bằng cách sửdụng các độđo đánh giá vềprecision, recall,
F1 và AUC.
24


---

Bảng 3: Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Information
Gain và GAN.
Dataset
Performance
Evaluation
Information Gain
VanillaGAN
CTGAN
WGANGP
RF
ET
AB
HGB
RF
ET
AB
HGB
RF
ET
AB
HGB
CM1
Precision
0.853
0.853
0.843
0.844
0.832
0.863
0.864
0.832
0.834
0.823
0.827
0.820
Recall
0.722
0.840
0.790
0.812
0.870
0.888
0.866
0.850
0.858
0.852
0.782
0.790
F1-score
0.769
0.843
0.812
0.826
0.847
0.865
0.861
0.839
0.844
0.836
0.801
0.802
AUC
0.671
0.695
0.644
0.658
0.671
0.695
0.662
0.627
0.633
0.63
0.621
0.638
KC1
Precision
0.797
0.808
0.811
0.808
0.815
0.807
0.810
0.809
0.814
0.795
0.804
0.802
Recall
0.836
0.830
0.841
0.832
0.845
0.832
0.840
0.836
0.827
0.796
0.807
0.789
F1-score
0.801
0.815
0.818
0.816
0.822
0.815
0.814
0.817
0.817
0.792
0.804
0.793
AUC
0.765
0.784
0.735
0.761
0.773
0.778
0.737
0.754
0.763
0.725
0.664
0.725
KC2
Precision
0.803
0.807
0.791
0.811
0.821
0.803
0.776
0.794
0.798
0.804
0.813
0.812
Recall
0.804
0.815
0.791
0.813
0.825
0.815
0.787
0.808
0.64
0.643
0.628
0.634
F1-score
0.800
0.807
0.789
0.807
0.807
0.801
0.778
0.796
0.661
0.668
0.655
0.657
AUC
0.777
0.791
0.726
0.792
0.812
0.788
0.651
0.783
0.765
0.788
0.737
0.767
PC1
Precision
0.893
0.918
0.899
0.907
0.881
0.924
0.909
0.911
0.879
0.890
0.878
0.889
Recall
0.892
0.915
0.907
0.917
0.919
0.932
0.922
0.922
0.799
0.877
0.818
0.858
F1-score
0.891
0.915
0.902
0.911
0.897
0.925
0.913
0.914
0.829
0.876
0.838
0.866
AUC
0.772
0.755
0.757
0.797
0.689
0.747
0.781
0.780
0.649
0.663
0.559
0.698
Average
Precision
0.836
0.846
0.836
0.843
0.837
0.849
0.840
0.836
0.831
0.828
0.830
0.830
Recall
0.813
0.850
0.832
0.844
0.864
0.867
0.854
0.854
0.781
0.792
0.759
0.768
F1-score
0.816
0.845
0.830
0.840
0.843
0.852
0.842
0.842
0.788
0.793
0.775
0.780
AUC
0.746
0.753
0.716
0.752
0.736
0.753
0.708
0.736
0.702
0.702
0.645
0.707
5.5.1
Kết quảthực nghiệm 1
Như đã được trình bày trong phần lý thuyết, 3 phương pháp lấy mẫu oversampling
khác nhau được sửdụng đểcân bằng 4 bộdữliệu với độđo phần mềm và 4 kỹ
thuật lựa chọn đặc trưng dựa trên filter có được áp dụng đểgiải quyết vấn đềlựa
chọn các thuộc tính tối ưu trong dựđoán lỗi. Hiệu suất của các mô hình dựđoán
lỗi với kỹthuật oversampling và lựa chọn đặc trưng dựa trên các dữliệu đã chọn
và đầy đủđộđo phần mềm được thểhiện trong Bảng 2-6. Hiệu suất trung bình
của bốn mô hình học máy (RF, ET, AB và HGB) cũng được tính toán đểkiểm tra
tính hiệu quảlựa chọn đặc trưng và lấy mẫu dữliệu trong dựđoán lỗi vềprecision,
recall, F1 và AUC. Từcác kết quảđược trình bày trong Bảng 2-6, có thểthấy
25


---

Bảng 4: Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Fisher và
GAN.
Dataset
Performance
Evaluation
Fisher
VanillaGAN
CTGAN
WGANGP
RF
ET
AB
HGB
RF
ET
AB
HGB
RF
ET
AB
HGB
CM1
Precision
0.833
0.842
0.836
0.828
0.845
0.837
0.836
0.840
0.818
0.814
0.828
HgB
Recall
0.674
0.838
0.766
0.794
0.850
0.866
0.816
0.852
0.788
0.852
0.746
0.832
F1-score
0.734
0.839
0.794
0.810
0.844
0.848
0.824
0.845
0.799
0.832
0.778
0.820
AUC
0.632
0.678
0.615
0.689
0.670
0.707
0.619
0.659
0.613
0.653
0.637
0.824
KC1
Precision
0.809
0.827
0.813
0.828
0.818
0.833
0.813
0.829
0.803
0.800
0.806
0.708
Recall
0.785
0.839
0.834
0.844
0.843
0.855
0.839
0.851
0.800
0.792
0.783
0.805
F1-score
0.794
0.832
0.819
0.833
0.823
0.836
0.819
0.835
0.798
0.795
0.793
0.773
AUC
0.763
0.798
0.749
0.770
0.783
0.798
0.748
0.778
0.755
0.747
0.686
0.785
KC2
Precision
0.795
0.810
0.794
0.825
0.784
0.792
0.795
0.794
0.818
0.827
0.806
0.755
Recall
0.783
0.811
0.794
0.830
0.8
0.811
0.809
0.815
0.675
0.664
0.628
0.829
F1-score
0.787
0.808
0.793
0.826
0.778
0.793
0.799
0.799
0.700
0.690
0.649
0.674
AUC
0.774
0.793
0.708
0.763
0.781
0.787
0.666
0.761
0.724
0.803
0.728
0.699
PC1
Precision
0.902
0.919
0.927
0.920
0.893
0.930
0.925
0.935
0.890
0.903
0.880
0.732
Recall
0.900
0.93
0.932
0.926
0.914
0.939
0.932
0.942
0.846
0.877
0.732
0.896
F1-score
0.900
0.922
0.926
0.922
0.899
0.932
0.927
0.935
0.865
0.883
0.785
0.851
AUC
0.867
0.808
0.817
0.889
0.749
0.816
0.867
0.879
0.700
0.732
0.611
0.868
Average
Precision
0.835
0.848
0.842
0.850
0.835
0.848
0.842
0.849
0.832
0.836
0.830
0.840
Recall
0.786
0.855
0.832
0.849
0.852
0.867
0.849
0.865
0.777
0.796
0.722
0.780
F1-score
0.804
0.850
0.833
0.848
0.836
0.852
0.842
0.853
0.790
0.800
0.751
0.794
AUC
0.759
0.769
0.722
0.778
0.746
0.776
0.725
0.769
0.698
0.734
0.666
0.733
rằng hiệu suất của phương pháp dựđoán các mô hình dựa trên sựkết hợp của 4
lựa chọn đặc trưng dựa trên filter và 2 mô hình lấy mẫu GAN (VanillaGAN và
CTGAN) đã đạt kết quảtốt hơn so với khi xây dựng mô hình dựđoán lỗi không
có lựa chọn đặc trưng và lấy mẫu dữliệu được sửdụng (như thểhiện trong Bảng
1). Ví dụ: giá trịAUC trung bình của mô hình dựđoán lỗi trên các tập dữliệu
gốc là 0,690, 0,711, 0,719 và 0,733 với mô hình RF, ET, AB và HGB tương ứng.
Từkết quảBảng 5, có thểquan sát thấy Relief và CTGAN đạt được hiệu suất
tốt hơn so với các kết hợp khác của kỹthuật lấy mẫu và lựa chọn đặc trưng dựa
trên filter khác với precision, recall, F1 và AUC trung bình cao nhất là 0,857 ,
0,873, 0,856 và 0,767 tương ứng trên Extra Tree. Tuy nhiên, sựkết hợp của từng
26


---

Bảng 5: Kết quảmô hình dựđoán lỗi phần mềm dựtrên kết hợp của Relief và
GAN.
Dataset
Performance
Evaluation
Relief
VanillaGAN
CTGAN
WGANGP
RF
ET
AB
HGB
RF
ET
AB
HGB
RF
ET
AB
HGB
CM1
Precision
0.845
0.848
0.843
0.835
0.824
0.872
0.855
0.844
0.829
0.834
0.839
0.831
Recall
0.696
0.808
0.784
0.788
0.866
0.890
0.860
0.866
0.828
0.864
0.752
0.814
F1-score
0.75
0.824
0.807
0.807
0.844
0.868
0.856
0.851
0.827
0.848
0.787
0.821
AUC
0.647
0.716
0.672
0.673
0.676
0.711
0.716
0.670
0.648
0.637
0.661
0.690
KC1
Precision
0.815
0.824
0.811
0.827
0.815
0.833
0.825
0.843
0.815
0.821
0.816
0.824
Recall
0.781
0.838
0.833
0.845
0.844
0.854
0.85
0.861
0.811
0.806
0.782
0.800
F1-score
0.793
0.829
0.819
0.833
0.821
0.836
0.828
0.847
0.810
0.807
0.792
0.805
AUC
0.773
0.798
0.737
0.776
0.788
0.797
0.757
0.788
0.759
0.746
0.720
0.740
KC2
Precision
0.811
0.789
0.789
0.798
0.781
0.802
0.785
0.789
0.816
0.809
0.797
0.812
Recall
0.794
0.804
0.791
0.804
0.804
0.817
0.798
0.806
0.658
0.651
0.609
0.642
F1-score
0.800
0.793
0.788
0.799
0.78
0.800
0.789
0.792
0.682
0.675
0.634
0.665
AUC
0.796
0.789
0.705
0.772
0.781
0.783
0.652
0.772
0.780
0.791
0.738
0.760
PC1
Precision
0.900
0.913
0.916
0.915
0.871
0.922
0.914
0.929
0.893
0.902
0.893
0.898
Recall
0.859
0.917
0.905
0.913
0.914
0.932
0.921
0.937
0.794
0.770
0.695
0.759
F1-score
0.873
0.914
0.909
0.912
0.89
0.921
0.915
0.928
0.823
0.798
0.747
0.800
AUC
0.782
0.783
0.839
0.814
0.691
0.775
0.841
0.802
0.680
0.707
0.646
0.685
Average
Precision
0.843
0.843
0.840
0.844
0.822
0.857
0.845
0.851
0.838
0.841
0.836
0.841
Recall
0.783
0.842
0.828
0.837
0.857
0.873
0.857
0.867
0.773
0.773
0.710
0.753
F1-score
0.804
0.840
0.831
0.838
0.834
0.856
0.847
0.855
0.785
0.782
0.740
0.773
AUC
0.757
0.767
0.738
0.759
0.734
0.767
0.742
0.758
0.717
0.720
0.691
0.719
kỹthuật lựa chọn đặc trưng (Chi-Squared, In- đội hình Gain, Fisher, Relief) và
WGAN tạo ra hiệu suất tương tựkhi không có kỹthuật lựa chọn đặc trưng và
lấy mẫu dữliệu nào được áp dụng. Khi so sánh các hiệu suất của phương pháp
WGANP với kỹthuật AdaBoost, chúng tôi thấy rằng giá trịAUC trung bình của
Chi-Squared, Information Gain, Fisher và Relief có giá trịAUC thấp nhất với lần
lượt là 0,645, 0,645, 0,666 và 0,691 như trong Bảng 2-6.
5.5.2
Kết quảthực nghiệm 2
Chúng tôi sửdụng tập dữliệu huấn luyện và kiểm tra riêng biệt cho mỗi lần lặp
lại thực nghiệm 10 lần; kết quảcuối cùng là trung bình của 10 lần lặp. Kết quả
27


---

Bảng 6: Kết quảso sánh của kết hợp các kỹthuật lựa chọn đặc trưng dựa trên
Wrapper và kỹluật lấy mẫu VanillaGAN.
Dataset
Performance
Evaluation
GA+VanillaGAN
PSO+VanillaGAN
WOA + VanillaGAN
Without FS
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR KNN RF
DT
NB
LR
CM1
Precision
0.808
0.790
0.804 0.750
0.859 0.806
0.813
0.81
0.805
0.833 0.821
0.782
0.808 0.803
0.829 0.792
0.780 0.801 0.749 0.800
Recall
0.726
0.829
0.811 0.734
0.786
0.740
0.860
0.849 0.863
0.686
0.754
0.860
0.837 0.866 0.706 0.707
0.825 0.811 0.803 0.876
F1-score
0.758
0.808
0.806 0.741
0.820
0.768
0.832 0.827 0.831
0.738
0.783
0.819
0.819 0.833 0.752 0.747
0.801 0.805 0.775 0.826
AUC
0.617
0.688
0.646 0.509
0.690
0.689
0.740 0.645 0.524
0.687
0.675
0.729
0.617 0.543
0.720 0.608
0.683 0.637 0.506 0.686
KC1
Precision
0.813
0.814
0.793 0.831
0.824
0.822
0.829
0.818 0.837 0.821
0.825
0.832
0.818 0.834
0.824 0.810
0.819 0.816 0.815 0.801
Recall
0.809
0.833
0.828 0.778
0.670
0.831
0.855 0.847 0.657
0.666
0.836
0.854 0.852 0.706
0.697 0.802
0.830 0.819 0.697 0.656
F1-score
0.811
0.818
0.804 0.797
0.713
0.825
0.817
0.819 0.701
0.710
0.828 0.816
0.821 0.741
0.735 0.805
0.810 0.813 0.751 0.701
AUC
0.726
0.789
0.769 0.783
0.755
0.746
0.817 0.795 0.769
0.744
0.741
0.804
0.790 0.780
0.766 0.715
0.785 0.763 0.764 0.799
KC2
Precision
0.869
0.876
0.882 0.879
0.884 0.881 0.879
0.870 0.871
0.876
0.874
0.879
0.876 0.884 0.872 0.866
0.863 0.866 0.872 0.870
Recall
0.841
0.875
0.862 0.745
0.693
0.866
0.924 0.913 0.900
0.789
0.866
0.922
0.913 0.907
0.793 0.817
0.884 0.857 0.879 0.769
F1-score
0.853
0.875
0.870 0.793
0.761
0.872
0.894 0.889 0.884
0.826
0.869
0.894 0.892 0.893
0.827 0.840
0.870 0.861 0.875 0.816
AUC
0.719
0.76
0.721 0.707
0.707
0.739
0.785 0.715 0.672
0.658
0.729
0.783 0.727 0.671
0.635 0.710
0.759 0.701 0.67
0.637
PC1
Precision
0.817
0.818
0.788 0.819
0.828
0.797
0.811
0.801 0.820
0.824
0.814
0.808
0.798 0.806
0.832 0.812
0.807 0.782 0.81
0.819
Recall
0.798
0.813
0.792 0.828 0.755
0.783
0.825
0.819 0.823
0.749
0.798
0.825
0.817 0.817
0.796 0.727
0.810 0.803 0.82
0.722
F1-score
0.804
0.811
0.784 0.816 0.774
0.789
0.811
0.789 0.818
0.769
0.800
0.806
0.797 0.808
0.807 0.767
0.808 0.792 0.814 0.767
AUC
0.772
0.804
0.738 0.817
0.820
0.760
0.826
0.817 0.818
0.817
0.788
0.806
0.798 0.772
0.819 0.770
0.767 0.737 0.74
0.809
JM1
Precision
0.747
0.766
0.758 0.768 0.759
0.747
0.762
0.757 0.764
0.750
0.742
0.749
0.747 0.762
0.761 0.738
0.747 0.742 0.756 0.740
Recall
0.768
0.809 0.806 0.796
0.704
0.774
0.807
0.805 0.785
0.555
0.768
0.770
0.776 0.796
0.591 0.766
0.760 0.777 0.785 0.511
F1-score
0.756
0.760
0.755 0.777
0.725
0.758
0.756
0.754 0.771
0.595
0.753
0.753
0.751 0.771
0.631 0.751
0.759 0.753 0.770 0.541
AUC
0.658
0.708 0.702 0.663
0.668
0.659
0.708
0.700 0.674
0.643
0.651
0.69
0.684 0.68
0.674 0.674
0.679 0.681 0.642 0.638
Average results
Precision
0.811
0.813
0.805 0.809
0.831
0.811
0.819 0.811 0.819
0.821
0.815
0.810
0.809 0.818
0.824 0.804
0.803 0.801 0.800 0.806
Recall
0.788
0.832
0.820 0.776
0.722
0.799
0.854 0.847 0.806
0.689
0.804
0.846
0.839 0.818
0.717 0.764
0.822 0.813 0.797 0.707
F1-score
0.796
0.814
0.804 0.785
0.759
0.802
0.822 0.816 0.801
0.728
0.807
0.818
0.816 0.809
0.750 0.782
0.810 0.805 0.797 0.730
AUC
0.698
0.750
0.715 0.696
0.728
0.719
0.775 0.734 0.691
0.710
0.717
0.762
0.723 0.689
0.723 0.695
0.735 0.704 0.664 0.714
FS: Feature Selection
đã được báo cáo trong Bảng 6 và Bảng 7, bao gồm năm kỹthuật học máy cho
kết quảtrung bình trong sốnăm bộdữliệu của mỗi phương pháp Wrapper tương
ứng các độđo hiệu suất được sửdụng. Đối với độđo đánh giá Precision, các giá
trịđạt được hầu như cao hơn 0.80 cho tất cảcác kỹthuật ngoại trừtập dữliệu
JM1, giá trịcao nhất là 0.884 đối với tập dữliệu PC1 trong cặp GA và WOA và
giá trịthấp nhất là 0.732 đối với tập dữliệu JM1 trong kỹthuật MA. Đối với độ
đo Recall, giá trịgần như cao hơn 0.80, cặp PSO và CS đạt mức cao nhất giá trị
0.924 đối với PC1 và giá trịthấp nhất là 0.591 đối với tập dữliệu JM1 trong kỹ
thuật WOA. Đối với độđo F1, BBA đạt giá trịcao nhất là 0.895 cho tập dữliệu
PC1, PSO và CS đạt giá trị0.894, cũng là mức tốt và giá trịthấp nhất là 0.40 đối
với tập dữliệu CM1. Vềmặt đo lường AUC, trong hầu hết các trường hợp, giá
trịlớn hơn hơn 0.700 ởCM1, PC1, KC1 và KC2. Giá trịAUC cao nhất là 0,826
28


---

Bảng 7: Kết quảso sánh của kết hợp các kỹthuật lựa chọn đặc trưng dựa trên
Wrapper và kỹluật lấy mẫu VanillaGAN (tt).
Dataset
Performance
Evaluation
MA+VanillaGAN
CS+VanillaGAN
BBA+ VanillaGAN
Without FS
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR KNN RF
DT
NB
LR
CM1
Precision
0.814
0.809
0.804 0.787
0.844 0.819
0.818
0.817 0.785
0.847 0.82
0.794
0.798 0.789
0.836 0.792
0.780 0.801 0.749 0.800
Recall
0.737
0.866
0.843 0.854
0.726
0.731
0.874
0.846 0.854
0.723
0.771
0.854
0.834 0.851 0.72
0.707
0.825 0.811 0.803 0.876
F1-score
0.769
0.83
0.82
0.818
0.768
0.766
0.839 0.828 0.816
0.766
0.792
0.82
0.813 0.817 0.763 0.747
0.801 0.805 0.775 0.826
AUC
0.676
0.708
0.644 0.542
0.727
0.683
0.744 0.671 0.568
0.715
0.686
0.727
0.623 0.538
0.689 0.608
0.683 0.637 0.506 0.686
KC1
Precision
0.818
0.84
0.825 0.828
0.824
0.829
0.823
0.815 0.833 0.819
0.817
0.834
0.817 0.813
0.824 0.810
0.819 0.816 0.815 0.801
Recall
0.829
0.859
0.853 0.721
0.688
0.829
0.853 0.848 0.666
0.673
0.827
0.858 0.849 0.663
0.673 0.802
0.830 0.819 0.697 0.656
F1-score
0.822
0.827
0.82
0.752
0.728
0.818
0.814
0.813 0.709
0.715
0.821 0.827
0.818 0.694
0.716 0.805
0.810 0.813 0.751 0.701
AUC
0.742
0.807
0.782 0.782
0.771
0.742
0.805 0.779 0.776
0.747
0.743
0.812
0.784 0.767
0.757 0.715
0.785 0.763 0.764 0.799
KC2
Precision
0.876
0.879
0.871 0.879
0.878 0.87
0.879
0.87
0.878
0.874
0.882
0.877
0.87
0.879 0.879 0.866
0.863 0.866 0.872 0.870
Recall
0.859
0.922
0.914 0.904
0.789
0.854
0.924 0.913 0.897
0.779
0.868
0.924
0.909 0.897
0.786 0.817
0.884 0.857 0.879 0.769
F1-score
0.867
0.894
0.89
0.89
0.827
0.861
0.894 0.889 0.887
0.818
0.874
0.895 0.887 0.886
0.824 0.840
0.870 0.861 0.875 0.816
AUC
0.717
0.789
0.716 0.665
0.659
0.716
0.79
0.72
0.675
0.652
0.736
0.801 0.719 0.669
0.652 0.710
0.759 0.701 0.67
0.637
PC1
Precision
0.797
0.807
0.782 0.817
0.823
0.783
0.824
0.829 0.826
0.83
0.827
0.815
0.785 0.812
0.828 0.812
0.807 0.782 0.81
0.819
Recall
0.774
0.823
0.794 0.825 0.747
0.758
0.819
0.825 0.832
0.766
0.809
0.826
0.806 0.821
0.787 0.727
0.810 0.803 0.82
0.722
F1-score
0.782
0.811
0.785 0.815 0.768
0.767
0.818
0.824 0.822
0.784
0.815
0.816
0.792 0.81
0.798 0.767
0.808 0.792 0.814 0.767
AUC
0.75
0.787
0.735 0.815
0.815
0.747
0.805
0.783 0.826
0.819
0.806
0.808
0.754 0.781
0.812 0.770
0.767 0.737 0.74
0.809
JM1
Precision
0.747
0.742
0.732 0.756 0.757
0.76
0.76
0.757 0.767
0.761
0.76
0.764
0.764 0.767
0.745 0.738
0.747 0.742 0.756 0.740
Recall
0.778
0.757 0.762 0.777
0.593
0.787
0.806
0.803 0.793
0.725
0.784
0.8
0.801 0.803
0.604 0.766
0.760 0.777 0.785 0.511
F1-score
0.756
0.745
0.741 0.764
0.63
0.769
0.758
0.759 0.776
0.74
0.769
0.765
0.76
0.774
0.642 0.751
0.759 0.753 0.770 0.541
AUC
0.654
0.679 0.668 0.655
0.669
0.666
0.72
0.709 0.663
0.672
0.686
0.709
0.703 0.682
0.651 0.674
0.679 0.681 0.642 0.638
Average results
Precision
0.81
0.815
0.803 0.813
0.825
0.812
0.821 0.818 0.818
0.826
0.821
0.817
0.807 0.812
0.822 0.804
0.803 0.801 0.800 0.806
Recall
0.795
0.845
0.833 0.816
0.709
0.792
0.855 0.847 0.808
0.733
0.812
0.852
0.84
0.807
0.714 0.764
0.822 0.813 0.797 0.707
F1-score
0.799
0.821
0.811 0.808
0.744
0.796
0.825 0.823 0.802
0.765
0.814
0.825
0.814 0.796
0.749 0.782
0.810 0.805 0.797 0.730
AUC
0.708
0.754
0.709 0.692
0.728
0.711
0.773 0.732 0.702
0.721
0.731
0.771
0.717 0.687
0.712 0.695
0.735 0.704 0.664 0.714
FS: Feature Selection
đối với KC2 trong phương pháp PSO và giá trịthấp nhất là 0,509 đối với CM1.
Ngoài ra, hiệu suất của các bộphân loại dựa trên các phương pháp lựa chọn tính
năng Wrapper tốt hơn so với với tập dữliệu gốc. Từkết quảtrung bình, có thể
thấy rằng PSO với Vanilla GAN và Cuckoo Search với VanillaGAN tạo ra các giá
trịtốt nhất và cao hơn các trường hợp khác trong hầu hết các trường hợp, tiếp
theo là Thuật toán Mayfly với Vanilla GAN.
6
Kết luận
Dữliệu nhiều chiều và các lớp không cân bằng là những yếu tốchính ảnh hưởng
đáng kểđến hiệu suất của các mô hình dựđoán lỗi phần mềm. Các kỹthuật lựa
chọn đặc trưng, chọn các tập hợp con dữliệu tối ưu, được áp dụng đểgiảm các
29


---

thuộc tính không liên quan đến lỗi và dư thừa. Các phương pháp lấy mẫu dữliệu
nhằm tạo ra các thểhiện của lớp mẫu mới và dữliệu cân bằng đã được nhiều nhà
nghiên cứu đềxuất đểgiải quyết vấn đềnày. Trong nghiên cứu này, chúng tôi thực
hiện phát triển các mô hình dựđoán lỗi hiệu quảbằng cách xửlý giải quyết vấn
đềmất cân bằng lớp và dư thừa đặc trưng một cách hiệu quả. Các biến thểGAN
đại diện cho các kỹthuật tiên tiến (CTGAN, Vanilla GAN và WANGGP) được áp
dụng đểlấy mẫu dữliệu khi xửlý dữliệu mất cân bằng. Sau đó, chúng tôi sửdụng
các kỹthuật lựa chọn đặc trưng (lựa chọn đặc trưng dựa trên filter và wrrapper)
trên các tập dữliệu cân bằng đểlựa chọn các đặc trưng tối ưu nhất trong dựđoán
lỗi. Các mô hình dựđoán lỗi được phát triển bằng cách sửdụng các mô hình phân
loại khác nhau sẽđược phân tích và hiệu suất của mô hình này được thực hiện
trên 5 bộdữliệu nguồn mở. Kết quảthửnghiệm cho thấy hiệu suất của các mô
hình dựđoán lỗi dựa trên sựkết hợp của Relief&CTGAN, PSO&VanillaGAN và
Cuckoo Search&VanillaGAN đạt được hiệu suất cao nhất trên hầu hết các tập dữ
liệu. Trong tương lai, chúng tôi dựđịnh khái quát hóa những phát hiện của các
mô hình đã trình vày đểtích hợp nhiều phương pháp lựa chọn đặc trưng và kỹ
thuật lấy mẫu dữliệu bằng cách sửdụng nhiều bộdữliệu lỗi phần mềm hơn.
30


---

References
[1] Aleksei Guryanov. <Histogram-based algorithm for building gradient boost-
ing ensembles of piecewise linear decision trees=. In: Analysis of Images, Social
Networks and Texts: 8th International Conference, AIST 2019, Kazan, Rus-
sia, July 17319, 2019, Revised Selected Papers 8. Springer. 2019, pp. 39350.
[2] Antonia Creswell et al. <Generative adversarial networks: An overview=. In:
IEEE signal processing magazine 35.1 (2018), pp. 53365.
[3] Avrim L Blum and Pat Langley. <Selection of relevant features and examples
in machine learning=. In: Artificial intelligence 97.1-2 (1997), pp. 2453271.
[4] Bartosz Krawczyk. <Learning from imbalanced data: open challenges and
future directions=. In: Progress in Artificial Intelligence 5.4 (2016), pp. 2213
232.
[5] Cagatay Catal and Banu Diri. <A systematic review of software fault pre-
diction studies=. In: Expert Systems with Applications 36.4 (2009), pp. 73463
7354. issn: 0957-4174. doi: https://doi.org/10.1016/j.eswa.2008.
10.027. url: https://www.sciencedirect.com/science/article/pii/
S0957417408007215.
[6] Chakkrit Tantithamthavorn, Ahmed E Hassan, and Kenichi Matsumoto.
<The impact of class rebalancing techniques on the performance and inter-
pretation of defect prediction models=. In: IEEE Transactions on Software
Engineering 46.11 (2018), pp. 120031219.
[7] Chris Seiffert et al. <RUSBoost: A hybrid approach to alleviating class im-
balance=. In: IEEE transactions on systems, man, and cybernetics-part A:
systems and humans 40.1 (2009), pp. 1853197.
[8] Christopher M. Bishop. Pattern Recognition and Machine Learning (Informa-
tion Science and Statistics). Berlin, Heidelberg: Springer-Verlag, 2006. isbn:
0387310738.
31


---

[9] Fei Wang, Jun Ai, and Zhuoliang Zou. <A cluster-based hybrid feature selec-
tion method for defect prediction=. In: 2019 IEEE 19th International Confer-
ence on Software Quality, Reliability and Security (QRS). IEEE. 2019, pp. 13
9.
[10] Girish Chandrashekar and Ferat Sahin. <A survey on feature selection meth-
ods=. In: Computers & Electrical Engineering 40.1 (2014), pp. 16328.
[11] Haidar Osman, Mohammad Ghafari, and Oscar Nierstrasz. <Automatic fea-
ture selection by regularization to improve bug prediction accuracy=. In: 2017
IEEE Workshop on Machine Learning Techniques for Software Quality Eval-
uation (MaLTeSQuE). IEEE. 2017, pp. 27332.
[12] Hamoud Aljamaan and Amal Alazba. <Software Defect Prediction Using
Tree-Based Ensembles=. In: Proceedings of the 16th ACM International Con-
ference on Predictive Models and Data Analytics in Software Engineering.
PROMISE 2020. Virtual, USA: Association for Computing Machinery, 2020,
pp. 1310. isbn: 9781450381277. doi: 10 . 1145 / 3416508 . 3417114. url:
https://doi.org/10.1145/3416508.3417114.
[13] Haonan Tong, Bin Liu, and Shihai Wang. <Software defect prediction using
stacked denoising autoencoders and two-stage ensemble learning=. In: Infor-
mation and Software Technology 96 (2018), pp. 943111.
[14] Hui Han, Wen-Yuan Wang, and Bing-Huan Mao. <Borderline-SMOTE: a new
over-sampling method in imbalanced data sets learning=. In: International
conference on intelligent computing. Springer. 2005, pp. 8783887.
[15] Ian Goodfellow et al. <Advances in neural information processing systems=.
In: Curran Associates, Inc 27 (2014), pp. 267232680.
[16] Isabelle Guyon and André Elisseeff. <An introduction to variable and feature
selection=. In: Journal of machine learning research 3.Mar (2003), pp. 11573
1182.
[17] Ishaan Gulrajani et al. <Improved Training of Wasserstein GANs=. In: Pro-
ceedings of the 31st International Conference on Neural Information Process-
32


---

ing Systems. NIPS’17. Long Beach, California, USA: Curran Associates Inc.,
2017, pp. 576935779. isbn: 9781510860964.
[18] Iyad Tumar et al. <Enhanced binary moth flame optimization as a feature
selection algorithm to predict software fault prediction=. In: Ieee Access 8
(2020), pp. 804138055.
[19] Jaechang Nam and Sunghun Kim. <CLAMI: Defect Prediction on Unlabeled
Datasets (T)=. In: 2015 30th IEEE/ACM International Conference on Auto-
mated Software Engineering (ASE). 2015, pp. 4523463. doi: 10.1109/ASE.
2015.56.
[20] Jaechang Nam et al. <Heterogeneous Defect Prediction=. In: IEEE Transac-
tions on Software Engineering 44.9 (2018), pp. 8743896. doi: 10.1109/TSE.
2017.2720603.
[21] Jelber Sayyad Shirabad and Tim Menzies. <The PROMISE Repository of
Software Engineering Databases.= In: 2005.
[22] Kai Ming Ting. <An instance-weighting method to induce cost-sensitive trees=.
In: IEEE Transactions on Knowledge and Data Engineering 14.3 (2002),
pp. 6593665.
[23] Kwabena Ebo Bennin et al. <Mahakil: Diversity based oversampling approach
to alleviate the class imbalance issue in software defect prediction=. In: IEEE
Transactions on Software Engineering 44.6 (2017), pp. 5343550.
[24] Kwabena Ebo Bennin et al. <The significant effects of data sampling ap-
proaches on software defect prioritization and classification=. In: 2017 ACM/IEEE
International Symposium on Empirical Software Engineering and Measure-
ment (ESEM). IEEE. 2017, pp. 3643373.
[25] Lei Qiao et al. <Deep learning based software defect prediction=. In: Neuro-
computing 385 (2020), pp. 1003110.
[26] Lei Xu and Kalyan Veeramachaneni. <Synthesizing tabular data using gen-
erative adversarial networks=. In: arXiv preprint arXiv:1811.11264 (2018).
33


---

[27] Lei Xu et al. <Modeling Tabular Data Using Conditional GAN=. In: Proceed-
ings of the 33rd International Conference on Neural Information Processing
Systems. Curran Associates Inc., 2019.
[28] Lillian J Ratliff, Samuel A Burden, and S Shankar Sastry. <Characteriza-
tion and computation of local Nash equilibria in continuous games=. In: 2013
51st Annual Allerton Conference on Communication, Control, and Comput-
ing (Allerton). IEEE. 2013, pp. 9173924.
[29] Lina Gong, Shujuan Jiang, and Li Jiang. <Tackling class imbalance problem in
software defect prediction through cluster-based over-sampling with filtering=.
In: IEEE Access 7 (2019), pp. 1457253145737.
[30] Mardhiya Hayaty, Siti Muthmainah, and Syed Muhammad Ghufran. <Ran-
dom and synthetic over-sampling approach to resolve data imbalance in clas-
sification=. In: International Journal of Artificial Intelligence Research 4.2
(2020), pp. 86394.
[31] Mark Lorenz and Jeff Kidd. Object-Oriented Software Metrics: A Practical
Guide. USA: Prentice-Hall, Inc., 1994. isbn: 013179292X.
[32] Martin Shepperd et al. <Data quality: Some comments on the nasa software
defect datasets=. In: IEEE Transactions on software engineering 39.9 (2013),
pp. 120831215.
[33] Maurice H. Halstead. Elements of Software Science (Operating and Program-
ming Systems Series). USA: Elsevier Science Inc., 1977. isbn: 0444002057.
[34] Meiliana et al. <Software metrics for fault prediction using machine learning
approaches: A literature review with PROMISE repository dataset=. In: 2017
IEEE International Conference on Cybernetics and Computational Intelli-
gence (CyberneticsCom). 2017, pp. 19323. doi: 10.1109/CYBERNETICSCOM.
2017.8311708.
[35] Mengmeng Zhu and Hoang Pham. <A two-phase software reliability modeling
involving with software fault dependency and imperfect fault removal=. In:
Computer Languages, Systems & Structures 53 (2018), pp. 27342.
34


---

[36] Michael J Siers and Md Zahidul Islam. <Novel algorithms for cost-sensitive
classification and knowledge discovery in class imbalanced datasets with an
application to NASA software defects=. In: Information Sciences 459 (2018),
pp. 53370.
[37] Mikel Galar et al. <A review on ensembles for the class imbalance problem:
bagging-, boosting-, and hybrid-based approaches=. In: IEEE Transactions
on Systems, Man, and Cybernetics, Part C (Applications and Reviews) 42.4
(2011), pp. 4633484.
[38] Ming Tan et al. <Online defect prediction for imbalanced data=. In: 2015
IEEE/ACM 37th IEEE International Conference on Software Engineering.
Vol. 2. IEEE. 2015, pp. 993108.
[39] Nathalie Japkowicz and Shaju Stephen. <The class imbalance problem: A
systematic study=. In: Intelligent data analysis 6.5 (2002), pp. 4293449.
[40] NC Shrikanth and Tim Menzies. <Assessing practitioner beliefs about soft-
ware defect prediction=. In: Proceedings of the ACM/IEEE 42nd International
Conference on Software Engineering: Software Engineering in Practice. 2020,
pp. 1823190.
[41] Nitesh V Chawla et al. <SMOTE: synthetic minority over-sampling tech-
nique=. In: Journal of artificial intelligence research 16 (2002), pp. 3213357.
[42] Noelia Sánchez-Maro˜no, Amparo Alonso-Betanzos, and María Tombilla-Sanromán.
<Filter methods for feature selection3a comparative study=. In: Lecture notes
in computer science 4881 (2007), pp. 1783187.
[43] Pierre Geurts, Damien Ernst, and Louis Wehenkel. <Extremely randomized
trees=. In: Machine learning 63 (2006), pp. 3342.
[44] Qinbao Song, Yuchen Guo, and Martin Shepperd. <A comprehensive investi-
gation of the role of imbalanced learning for software defect prediction=. In:
IEEE Transactions on Software Engineering 45.12 (2018), pp. 125331269.
35


---

[45] R Muthukrishnan and R Rohini. <LASSO: A feature selection technique in
predictive modeling for machine learning=. In: 2016 IEEE international con-
ference on advances in computer applications (ICACA). IEEE. 2016, pp. 183
20.
[46] Rohit Singh and Santosh Singh Rathore. <Linear and non-linear bayesian
regression methods for software fault prediction=. In: International Journal
of System Assurance Engineering and Management 13.4 (2022), pp. 18643
1884.
[47] Ron Kohavi and George H John. <Wrappers for feature subset selection=. In:
Artificial intelligence 97.1-2 (1997), pp. 2733324.
[48] Ruchika Malhotra and Shine Kamal. <An empirical study to investigate over-
sampling methods for improving software defect prediction using imbalanced
data=. In: Neurocomputing 343 (2019), pp. 1203140.
[49] Ruchika Malhotra. <A systematic review of machine learning techniques for
software fault prediction=. In: Applied Soft Computing 27 (2015), pp. 5043
518.
[50] Ruud JG Van Sloun et al. <Deep learning for super-resolution vascular ultra-
sound imaging=. In: ICASSP 2019-2019 IEEE International Conference on
Acoustics, Speech and Signal Processing (ICASSP). IEEE. 2019, pp. 10553
1059.
[51] S.R. Chidamber and C.F. Kemerer. <A metrics suite for object oriented de-
sign=. In: IEEE Transactions on Software Engineering 20.6 (1994), pp. 4763
493. doi: 10.1109/32.295895.
[52] Safa Omri and Carsten Sinz. <Deep Learning for Software Defect Prediction:
A Survey=. In: Proceedings of the IEEE/ACM 42nd International Conference
on Software Engineering Workshops. ICSEW’20. Seoul, Republic of Korea:
Association for Computing Machinery, 2020, pp. 2093214. isbn: 9781450379632.
doi: 10 . 1145 / 3387940 . 3391463. url: https : / / doi . org / 10 . 1145 /
3387940.3391463.
36


---

[53] Santosh S Rathore and Sandeep Kumar. <A study on software fault prediction
techniques=. In: Artificial Intelligence Review 51 (2019), pp. 2553327.
[54] Santosh Singh Rathore et al. <Generative Oversampling Methods for Han-
dling Imbalanced Data in Software Fault Prediction=. In: IEEE Transactions
on Reliability 71.2 (2022), pp. 7473762.
[55] Shamsul Huda et al. <An ensemble oversampling model for class imbalance
problem in software defect prediction=. In: IEEE access 6 (2018), pp. 241843
24195.
[56] Shuo Feng et al. <COSTE: Complexity-based OverSampling TEchnique to
alleviate the class imbalance problem in software defect prediction=. In: In-
formation and Software Technology 129 (2021), p. 106432.
[57] Simon Haykin. Neural networks: a comprehensive foundation. Prentice Hall
PTR, 1998.
[58] Sina Fathi-Kazerooni and Roberto Rojas-Cessa. <Gan tunnel: Network traffic
steganography by using gans to counter internet traffic classifiers=. In: Ieee
Access 8 (2020), pp. 1253453125359.
[59] T.J. McCabe. <A Complexity Measure=. In: IEEE Transactions on Software
Engineering SE-2.4 (1976), pp. 3083320. doi: 10.1109/TSE.1976.233837.
[60] Tero Karras et al. <Progressive growing of gans for improved quality, stability,
and variation=. In: arXiv preprint arXiv:1710.10196 (2017).
[61] Thomas Zimmermann, Rahul Premraj, and Andreas Zeller. <Predicting de-
fects for eclipse=. In: Third International Workshop on Predictor Models in
Software Engineering (PROMISE’07: ICSE Workshops 2007). IEEE. 2007,
pp. 939.
[62] Tianqi Chen and Carlos Guestrin. <XGBoost: A Scalable Tree Boosting Sys-
tem=. In: Proceedings of the 22nd ACM SIGKDD International Conference
on Knowledge Discovery and Data Mining. KDD ’16. San Francisco, Califor-
nia, USA: Association for Computing Machinery, 2016, pp. 7853794. isbn:
37


---

9781450342322. doi: 10.1145/2939672.2939785. url: https://doi.org/
10.1145/2939672.2939785.
[63] Tracy Hall and David Bowes. <The state of machine learning methodology in
software fault prediction=. In: 2012 11th international conference on machine
learning and applications. Vol. 2. IEEE. 2012, pp. 3083313.
[64] Tracy Hall et al. <A Systematic Literature Review on Fault Prediction Per-
formance in Software Engineering=. In: IEEE Transactions on Software En-
gineering 38 (2012), pp. 127631304.
[65] Yasutaka Kamei et al. <The effects of over and under sampling on fault-prone
module detection=. In: First international symposium on empirical software
engineering and measurement (ESEM 2007). IEEE. 2007, pp. 1963204.
[66] Yibiao Yang et al. <Effort-Aware Just-in-Time Defect Prediction: Simple Un-
supervised Models Could Be Better than Supervised Models=. In: Proceedings
of the 2016 24th ACM SIGSOFT International Symposium on Foundations
of Software Engineering. FSE 2016. Seattle, WA, USA: Association for Com-
puting Machinery, 2016, pp. 1573168. isbn: 9781450342186. doi: 10.1145/
2950290.2950353. url: https://doi.org/10.1145/2950290.2950353.
[67] Yoav Freund. <Boosting a weak learning algorithm by majority=. In: Infor-
mation and computation 121.2 (1995), pp. 2563285.
[68] Zhanqi Cui et al. <Improving software fault localization by combining spec-
trum and mutation=. In: IEEE Access 8 (2020), pp. 1722963172307.
[69] Zhiqiang Li, Xiao-Yuan Jing, and Xiaoke Zhu. <Progress on approaches to
software defect prediction=. In: Iet Software 12.3 (2018), pp. 1613175.
[70] Zhiyuan Wan et al. <Perceptions, expectations, and challenges in defect pre-
diction=. In: IEEE Transactions on Software Engineering 46.11 (2018), pp. 12413
1266.
[71] url: http://promise.site.uottawa.ca/SERepository/datasets-page.
html.
38


---

A comparative study of Wrapper feature selection
techniques in Software Fault Prediction
Nguyen Thanh Long1 and Ha Thi Minh Phuong2 Nguyen Thanh
Binh3[0000−0002−0154−1162]
1 The University of Danang - University of Science and Technology
2
3 The University of Danang - Vietnam-Korea University of Information and
Communication Technology, Danang
ngthlo.doc@gmail.com
htmphuong@vku.udn.vn
ntbinh@vku.udn.vn
Abstract. Software fault prediction aims to classify whether the module
is defective or not-defective. In software systems, there are some software
metrics may contain irrelevant or redundant information that leads to
negative impact on the performance of the fault prediction model. There-
fore, feature selection is an method that several studies have addressed to
reduce computation time, improve prediction performance and provide a
better understanding of data in machine learning. Additionally, the pres-
ence of imbalanced classes is one of the most challenge in software fault
prediction. In this study, we examined the eﬀectiveness of six diﬀerent
wrapper feature selection including Genetic Algorithm, Particle Swarm
Optimization, Whale Optimization Algorithm, Cuckoo Search, Mayﬂy
Algorithm and Binary Bat Algorithm for selecting the optimal subset of
features. Then, we applied VanilaGAN to train the dataset with optimal
features for handling the imbalanced problem. Subsequently, these gener-
ated training dataset and the tesing dataset are fed to the machine learn-
ing techniques. Experimental validation has been done on ﬁve dataset
collected from Promise repository and Precision, Recall, F1-score, and
AUC are evaluation performance measurements.
Keywords: Software fault prediction, feature selection, Wrapper, Vanil-
laGAN, dataset
1
Introduction
Software defect prediction (SDP) is a signiﬁcant procedure in software engi-
neering that aims to identify potential defects in software systems before they
occur. The robust software predictive model predicts correctly bugs or defects
before releasing a new software version. Therefore, developers can eﬀectively
plan the distribution of testing eﬀort to reduce the overall cost of software de-
velopment and improve the quality and reliability of the ﬁnal product.
In recent studies, machine learning techniques have been exploited widely


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
to construct a fault prediction model. These techniques use the historical de-
fect dataset that has been collected from previous software projects to make
predictions about the occurrence of future defects. The defect dataset consists
of various software features (software metrics) e.g.,Response for a Class, Depth
of inheritance tree or Line of Code and labels which indicates defective or not
for each module. During training, the predictive model learns the characteris-
tics of software projects and makes predictions whether new module is faulty
or not faulty [24].Several researches state that the performance of software fault
prediction models depends on software fault dataset [14, 2]. However, there are
two major challenges that the software defect prediction dataset faces the high
dimensional features and imbalanced classes [22]. Additionally, some software
metrics are irrelevant or redundant to fault-proneness modules. They are the
most signiﬁcant reasons that reduce the eﬀectiveness of used machine learning
techniques in SFP.
In SFP literature, feature selection is employed to address the problem of
minimizing the redundant and irrelevant features that are not useful for predic-
tion. The objective of feature selection is to generate a subset of optimal metrics
from the input data to achieve better prediction performance [5]. Numerous fea-
ture selection techniques have been proposed in software fault prediction domain
[10, 19]. Feature selection techniques can be broadly categorized into three types,
namely ﬁlter, wrapper and embedded techniques. The ﬁlter technique involves
applying a statistical measure to each feature and selecting the top features
based on their scores. Wrapper methods use a machine learning algorithm to
evaluate the performance of a subset of features. The algorithm is trained us-
ing diﬀerent subsets of features and the subset that yields the best performance
is selected. Embedded methods incorporate feature selection into the learning
algorithm itself. For example, some machine learning algorithms have built-in
feature selection mechanisms, such as Lasso regression, decision trees, and ran-
dom forests. According to Savina Colaco et al. [6], wrapper-based technique is
the most popular use across all feature selection methods.
In this study, we examine the performance of diﬀerent wrapper feature se-
lection methods including Genetic Algorithm (GA), The Particle Swarm Opti-
mization (PSO), Whale Optimization Algorithm (WOA), Cuckoo Search (CS),
Mayﬂy Algorithm (MA) and Binary Bat Algorithm. Our main contribution is
to evaluate the eﬀectiveness of various wrapper feature selection techniques and
compare the performance of classiﬁers in generating the optimal variables for
the classiﬁcation of software faults.
The remainder of this study is organized as follows: section 2 presents the
previous works related to current research. Used wrapper feature selection tech-
niques are introduced in Section 3. Section 4 presents the proposed methodology
followed by the experimental results in Section 5. Section 6 concludes the study
with a discussion of our results and prospects for future work.


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
2
Related Work
Feature selection is one of the most signiﬁcant tasks of preprocessing data in
software fault prediction. The objective of feature selection is to select a subset of
optimal features that excludes irrelevant or redundant features. Recently, several
studies have proposed diﬀerent feature selection techniques in SFP. Khoshgoftaar
et al. [12] compared diﬀerent ﬁlter feature-ranking selection techniques, namely
information gain (IG), ReliefF, chi-squared (CS), symmetrical uncertainty (SU)
and gainratio (GR) using 16 fault datasets. They also considered the signal-to-
noise ratio (SNR) which is infrequently employed as software metric. Throughout
the experimental results, the author suggested IG and SNR achieved the best
classiﬁcation performance across all datasets. However, Khoshgoftaar also rec-
ommended that although feature selection can improve the performance of fault
prediction models but it has not yet addressed the imbalanced data problem.
Wang [27] performed a study to address the problem of which feature elimination
methods are stable in case of data change (the deletion or addition of features).
They examined various ﬁlter-based and wrapper-based feature subset selection
techniques using three real-world fault datasets. From the experimental results,
they showed that the Correlation-Based Feature Selection (CFS) is the most sta-
ble method among diﬀerent methods. Mohammad et al. [13] demonstrated the
combination of feature selection and ensemble learning had a great performance
of fault classiﬁcation. They also concluded that greedy forward selection pro-
vided better performance than other methods and average probability ensemble
which grouped seven devised classiﬁers outperformed conventional methods such
as random forest and weighted SVMs. Wang [26] proposed a Cluster-based Hy-
brid Feature Selection that combined Filter and Wrapper methods to reduce the
irrelevant and redundant information and enhance the performance the of predic-
tive model. Their experimental results indicated that the Cluster-based Hybrid
Feature Selection method obtained better performance compared to the other
traditional methods in terms of accuracy evaluation measure. Savina Colaco et.al
[6] presented a survey of diﬀerent feature selection techniques speciﬁcally ﬁlter,
wrapper and embedded methods. They found that wrapper methods indicated
notable improvement in accuracy for the dataset containing larger features, hence
wrapper methods are more popularly applied to obtain optimal features than
other methods. Ghost et al. [10] proposed a hybrid of wrapper and ﬁlter feature
selection based on ant colony optimization. They demonstrated their proposed
method outperformed most of the modern methods used for feature selection.
3
Feature Selection
Feature selection is a high dimensionality reduction method by selecting the
most important and relevant features, which is the smallest set from a large
set of features in the given dataset. There are three types of feature selection
methods including the Filter method, Wrapper method and Embedded method.
In this study, Wrapper methods are adopted to select relevant features from


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
the Promise dataset. Additionally, the features of the software fault dataset are
deﬁned as software metrics. Therefore, in this section, we concentrate on the
software metrics and wrapper-based feature selection.
3.1
Software Metrics
Various kinds of features indicate the characteristic of software. Software met-
rics are used to evaluate various aspects of software development and software
characteristics, such as software quality, complexity, performance, and maintain-
ability. These metrics provide valuable insights into the development process and
can help identify areas for improvement.
Software metrics can be broadly divided into four categories: Procedure,
Object-Oriented, Hybrid and Miscellaneous Metrics [4, 17]. Procedure software
metrics typically focus on the internal characteristics of software, such as its size,
complexity, and maintainability. Some examples of traditional software metrics
are Line Of Code (LOC), McCabe [16] and Halstead Metrics [11]. Object-oriented
(OO) metrics are applied to measure the properties of object oriented software
such as Coupling between Objects (CBO), Depth of inheritance tree (DIT),
Number of children (NOC), Response for a Class [1]. Software hybrid metrics
are a set of software metrics that combine elements of traditional and object-
oriented metrics to provide a more comprehensive view of software quality and
complexity [15]. Hybrid metrics are designed to measure both the internal and
external characteristics of software, such as its functionality, usability, and main-
tainability. Some common hybrid metrics [25, 7] include Function point analysis
(FPA), Maintainability index (MI). Miscellaneous metrics are process metrics [8],
change metrics [18], etc. According to the research ’s Ruchika Malhotra [15], the
most commonly used metrics are recorded in the procedure and object-oriented
metrics.
3.2
Genetic Algorithm
Genetic algorithm (GA) is an optimization algorithm that is inspired by nat-
ural selection. It is a population-based search algorithm that utilizes the concept
of survival of the ﬁttest. The new populations are produced by iterative use of
genetic operators on individuals present in the population. The chromosome rep-
resentation, selection, crossover, mutation, and ﬁtness function computation are
the key elements of GA.
3.3
Particle Swarm Optimization
Particle Swarm Optimization was proposed by Kennedy and Eberhart in
1995. This method is inspired by the habits of sharing information from ﬁnd-
ing food processes of a school of ﬁsh or ﬂock of birds that move in a group.
In a PSO algorithm, particles (which represent candidate solutions) are ﬂying
around, in a multi-dimensional search space. The positions of these particles are
adjusted according to the particles’ own memories and the best-ﬁt particle of
the neighboring particles.[21].


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
3.4
Whale Optimization Algorithm
Whale optimization algorithm (WOA) is a nature-inspired meta-heuristic
optimization algorithm that mimics the hunting behavior of humpback whales.
The algorithm is inspired by the bubble-net hunting strategy. Foraging behavior
of Humpback whales is called the bubble-net feeding method. Humpback whales
prefer to hunt schools of krill or small ﬁshes close to the surface. We can start
WOA with a random initialization of the search agents and choose the best,
ﬁrst solution by calculating the ﬁtness of each search agent. Next, the position is
updated by basing on equations of Spiral Bubble-Net Feeding Behavior method
and then search space constraints are checked and the best solution is updated
if there is a better one found. Finally, the algorithm loop is terminated by the
maximum number of iterations (default criterion) [3].
3.5
Cuckoo Search
Cuckoo search (CS) is a meta-heuristic algorithm inspired by the bird cuckoo,
these are the "Brood parasites" birds. In a nest, each egg represents a solution
and the cuckoo egg represents a new and good solution. The obtained solution
is a new solution based on the existing one and the modiﬁcation of some char-
acteristics. In CS algorithm, there are three rules: 1) Each cuckoo lays one egg
at a time, and dumps its egg in randomly chosen nest; 2) The best nests with
high quality of eggs will carry over to the next generations; 3) The number of
available host nests is ﬁxed, and the egg laid by a cuckoo is discovered by the
host bird with a probability pa ∈[0, 1]. In this case, the host bird can either
throw the egg away or abandon the nest, and build a completely new nest [28].
3.6
Mayﬂy Algorithm
Inspired from the ﬂight behavior and the mating process of mayﬂies, the
Mayﬂy Algorithm (MA) combines major advantages of swarm intelligence and
evolutionary algorithms [29]. In MA, the mayﬂy swarms would be separated
into male and female individuals. Specially, the male mayﬂies would always be
strong and consequently, resulting in a better performance in optimization. And
the individuals in MA would update their position according to their current
position and velocity the same way as the individuals in PSO. All of the male
mayﬂies and female mayﬂies would update their positions with the same mea-
sure. However, their velocity would be updated in diﬀerent ways. The velocity
of mayﬂies would be updated according to their current ﬁtness values and the
historical best ﬁtness values due to the responsibility of carrying on exploration
or exploitation procedures during iterations. The female mayﬂies would update
their velocities with a diﬀerent style, they would update their velocities based
on the male mayﬂies they want to mate because of a short life cycle within seven
days. All of the top half of female and male mayﬂies would be mated and given a
pair of children for every one of them. Their oﬀspring would be randomly evolved


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
from their parents:
offsrping1 = L ∗male + (1 −L) ∗female
(1)
offspring2 = L ∗female + (1 −L) ∗male
(2)
where, L are random numbers in Gauss distribution [9].
3.7
Binary Bat Algorithm
Based on the bat’s behaviour, an interesting meta-heuristic optimization
technique called Bat Algorithm was developed. Such technique has been de-
veloped to behave as a band of bats tracking prey/foods using their capability
of echolocation. In order to model this algorithm, some rules had been idealized,
as follows: 1) All bats use echolocation to sense distance, and they also “know”
the diﬀerence between food/prey and background barriers in some magical way;
2) A bat bi ﬂy randomly with velocity vi at position xi with a ﬁxed frequency
fmin, varying wavelength and loudness A0 to search for prey. They can auto-
matically adjust the wavelength (or frequency) of their emitted pulses and adjust
the rate of pulse emission r ∈[0, 1], depending on the proximity of their target;
3) Although the loudness can vary in many ways, the loudness varies from a
large (positive) was assumed that A0 to a minimum constant value Amin. In
feature selection, since the problem is to select or not a given feature, the bat’s
position is then represented by binary vectors restricting the new bat’s position
to only binary values using a sigmoid function (BBA) [20].
3.8
Feature Selection Details
In order to select features eﬀectively, we taked advantage of feature selection
module of sklearn library developed in Python that provides many machine
learning algorithms. For the GA, we use 10 number of agents, cross and mutation
probability are set to 0.7 and 0.1 correspondingly. For the rest, just one agents is
used in selection process. Finally, log2(S) is set to max iterations of each method,
where S is the number of samples.
4
Methodology
4.1
Proposed Approach
As we mentioned in introduction, software fault prediction is a vital proce-
dure in software engineering and also depends on historical datasets that have
been collected from previous software projects. And this process still has two ma-
jor challenges including high dimensional data and imbalanced classes. Therefore
we propose an approach to examine the the eﬀectiveness of six diﬀerent Wrapper
methods for selecting the subset of optimal features. Then the variant of gen-
erative adversarial network - VanillaGAN [23] is applied to generate synthetic


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
instances of faulty modules to balance the ratio of faulty and non-faulty modules
in the fault datasets.
The overall approach is shown in Fig.1. In data preprocessing stage, we ﬁll
the missing values and apply Z-normalization for data normalization. Next, we
apply six diﬀerent wrapper methods, namely GA, PSO, WOA, CS, MA and BBA
to select the most important and relevant features for reducing high dimension
features. The datasets with optimal features are used to train the VanillaGAN
network to overcome the imbalanced data. Finally, these training datsets, and
testing datasets are used to train using machine learning techniques, e.g K-
Nearest Neighbors (KNN), Random Forest (RF), Decision Tree (DT), Naïve
Bayes (NB) and Logistic Regression (LR). We use precision, recall, F1-score and
AUC as measures to evaluate the performance of diﬀerent wrapper-based feature
selection methods.
Fig. 1. Flow diagram of proposed approach
4.2
VanillaGAN for Handling imbalanced data
We use Vanilla Gan, which is the simplest version of GAN. The generator
network lean the probability of the training set by mapping the noise z which
is drawn independent and identically distributed (i.i.d) from N (0, 0.01) and
added to both real and synthetic data to the probability distribution of train-
ing samples. Then, synthetic samples that are closer possible to real samples
were generated by the generator network. It uses backpropagation to train both
models. In Vanilla GAN, we use neural networks to approximate complex, high-
dimensional distributions for both Gen and Dis. The discriminator training is
done by minimizing its prediction error, whereas the generator is trained by
maximizing the prediction error by the discriminator. This can be formalized as
given follows:
min(ΘGen)max(ΘDis)(Ex∼pD[logDis(x)] + Ez∼pz[log(1 −Dis(Gen(z)))])
(3)
where pD is the real data distribution, pz is the prior distribution of the gener-
ative network, and ΘGen and ΘDis are the parameters of the generator (Gen)


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
and discriminator (Dis). Given a strong discriminator, the generator’s goal is
achieved if pD, the generator’s distribution over x, equals pz , the real distri-
bution, which means that the Jensen–Shannon Divergence (JSD) is minimized
[23].
4.3
Dataset
In this study, we used ﬁve sub-datasets collected from PROMISE repository
which are collections of publicly available datasets. These resources are adopted
to serve researchers in building predictive software models and the software
engineering community at large. In terms of software fault prediction (SFP)
problems, the datasets provide independent variables which are the diﬀerent
source code metrics such as line count of code (loc), coupling between objects
(CBO), etc., and dependent variable in faulty and non-faulty with labels (0) and
(1) correspondingly. The details of the used datasets are given in Table 1.
Table 1. Description of used software fault datasets
Dataset
Release
Instances
Metric
Faulty Instances
Imbalanced
ratio (%)
PROMISE
CM1
505
40
48
9.504
KC1
2107
21
325
15.424
KC2
522
20
107
20.498
PC1
1107
40
76
6.865
JM1
10885
20
2106
19.347
4.4
Evaluation Measurement
Performance evaluation measures such as Precision, Recall, F1-score and
AUC are used to evaluate how the wrapper feature selection algorithms aﬀect
the performance of prediction models. Precision is the ratio between the True
Positive and all the Positive, meanwhile Recall is the measure of our model cor-
rectly identifying True Positive. In software fault prediction problems, Precision
would be the measure of instances that our model correctly identiﬁes as faulty
labels out of all instances actually are faulty labels. For all instances which ac-
tually are faulty labels, Recall tells us how many instances our model correctly
identiﬁes as faulty labels. These metrics are deﬁned by the following:
Precision(P) =
TP
TP + TF , Recall(R) =
TP
TP + FN
(4)


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
where TP = True positive, FP = False positive, FN = False negative. From
two values of Precision and Recall, we can calculate additional metrics that are
F1-score and AUC:
F1 −score = 2 ∗P ∗R
P + R
(5)
The F1-score is the harmonic mean of the Precision and Recall. The highest
possible value of an F-score is 1.0, indicating perfect precision and recall, and
the lowest possible value is 0, if either precision or recall are zero. Besides that,
AUC calculates the area under the receiver operating characteristics(ROC). This
metric represents the probability that a random positive instance to the right of
a random negative instance. The higher the probability is, the more perfect the
prediction is.
5
Experimental Result
We use a separate training and testing dataset for each repetition of 10-time
experiments; the ﬁnal result is the average of the 10 iterations. The result has
been reported in Table 2 and Table 3, including ﬁve machine learning techniques
for the average result of ﬁve datasets of each Wrapper method with regard to
used performance measures.
Dataset Performance
Evaluation
GA+VanillaGAN
PSO+VanillaGAN
WOA + VanillaGAN
Without FS
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR KNN RF
DT
NB
LR
CM1
Precision
0.808 0.790 0.804 0.750 0.859 0.806 0.813 0.81
0.805 0.833 0.821 0.782 0.808 0.803 0.829 0.792 0.780 0.801 0.749 0.800
Recall
0.726 0.829 0.811 0.734 0.786 0.740 0.860 0.849 0.863 0.686 0.754 0.860 0.837 0.866 0.706 0.707 0.825 0.811 0.803 0.876
F1-score
0.758 0.808 0.806 0.741 0.820 0.768 0.832 0.827 0.831 0.738 0.783 0.819 0.819 0.833 0.752 0.747 0.801 0.805 0.775 0.826
AUC
0.617 0.688 0.646 0.509 0.690 0.689 0.740 0.645 0.524 0.687 0.675 0.729 0.617 0.543 0.720 0.608 0.683 0.637 0.506 0.686
KC1
Precision
0.813 0.814 0.793 0.831 0.824 0.822 0.829 0.818 0.837 0.821 0.825 0.832 0.818 0.834 0.824 0.810 0.819 0.816 0.815 0.801
Recall
0.809 0.833 0.828 0.778 0.670 0.831 0.855 0.847 0.657 0.666 0.836 0.854 0.852 0.706 0.697 0.802 0.830 0.819 0.697 0.656
F1-score
0.811 0.818 0.804 0.797 0.713 0.825 0.817 0.819 0.701 0.710 0.828 0.816 0.821 0.741 0.735 0.805 0.810 0.813 0.751 0.701
AUC
0.726 0.789 0.769 0.783 0.755 0.746 0.817 0.795 0.769 0.744 0.741 0.804 0.790 0.780 0.766 0.715 0.785 0.763 0.764 0.799
KC2
Precision
0.869 0.876 0.882 0.879 0.884 0.881 0.879 0.870 0.871 0.876 0.874 0.879 0.876 0.884 0.872 0.866 0.863 0.866 0.872 0.870
Recall
0.841 0.875 0.862 0.745 0.693 0.866 0.924 0.913 0.900 0.789 0.866 0.922 0.913 0.907 0.793 0.817 0.884 0.857 0.879 0.769
F1-score
0.853 0.875 0.870 0.793 0.761 0.872 0.894 0.889 0.884 0.826 0.869 0.894 0.892 0.893 0.827 0.840 0.870 0.861 0.875 0.816
AUC
0.719 0.76
0.721 0.707 0.707 0.739 0.785 0.715 0.672 0.658 0.729 0.783 0.727 0.671 0.635 0.710 0.759 0.701 0.67
0.637
PC1
Precision
0.817 0.818 0.788 0.819 0.828 0.797 0.811 0.801 0.820 0.824 0.814 0.808 0.798 0.806 0.832 0.812 0.807 0.782 0.81
0.819
Recall
0.798 0.813 0.792 0.828 0.755 0.783 0.825 0.819 0.823 0.749 0.798 0.825 0.817 0.817 0.796 0.727 0.810 0.803 0.82
0.722
F1-score
0.804 0.811 0.784 0.816 0.774 0.789 0.811 0.789 0.818 0.769 0.800 0.806 0.797 0.808 0.807 0.767 0.808 0.792 0.814 0.767
AUC
0.772 0.804 0.738 0.817 0.820 0.760 0.826 0.817 0.818 0.817 0.788 0.806 0.798 0.772 0.819 0.770 0.767 0.737 0.74
0.809
JM1
Precision
0.747 0.766 0.758 0.768 0.759 0.747 0.762 0.757 0.764 0.750 0.742 0.749 0.747 0.762 0.761 0.738 0.747 0.742 0.756 0.740
Recall
0.768 0.809 0.806 0.796 0.704 0.774 0.807 0.805 0.785 0.555 0.768 0.770 0.776 0.796 0.591 0.766 0.760 0.777 0.785 0.511
F1-score
0.756 0.760 0.755 0.777 0.725 0.758 0.756 0.754 0.771 0.595 0.753 0.753 0.751 0.771 0.631 0.751 0.759 0.753 0.770 0.541
AUC
0.658 0.708 0.702 0.663 0.668 0.659 0.708 0.700 0.674 0.643 0.651 0.69
0.684 0.68
0.674 0.674 0.679 0.681 0.642 0.638
Average results
Precision
0.811 0.813 0.805 0.809 0.831 0.811 0.819 0.811 0.819 0.821 0.815 0.810 0.809 0.818 0.824 0.804 0.803 0.801 0.800 0.806
Recall
0.788 0.832 0.820 0.776 0.722 0.799 0.854 0.847 0.806 0.689 0.804 0.846 0.839 0.818 0.717 0.764 0.822 0.813 0.797 0.707
F1-score
0.796 0.814 0.804 0.785 0.759 0.802 0.822 0.816 0.801 0.728 0.807 0.818 0.816 0.809 0.750 0.782 0.810 0.805 0.797 0.730
AUC
0.698 0.750 0.715 0.696 0.728 0.719 0.775 0.734 0.691 0.710 0.717 0.762 0.723 0.689 0.723 0.695 0.735 0.704 0.664 0.714
FS: Feature Selection
Table 2. Comparison results of presented Wrapper feature selection techniques com-
bined with Vanilla GAN for all the used dataset.
For the Precision measure, values are almost higher than 0.80 for all the
techniques except JM1 dataset, the highest value is 0.884 for the PC1 dataset


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
Dataset Performance
Evaluation
MA+VanillaGAN
CS+VanillaGAN
BBA+ VanillaGAN
Without FS
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR
KNN
RF
DT
NB
LR KNN RF
DT
NB
LR
CM1
Precision
0.814 0.809 0.804 0.787 0.844 0.819 0.818 0.817 0.785 0.847 0.82
0.794 0.798 0.789 0.836 0.792 0.780 0.801 0.749 0.800
Recall
0.737 0.866 0.843 0.854 0.726 0.731 0.874 0.846 0.854 0.723 0.771 0.854 0.834 0.851 0.72
0.707 0.825 0.811 0.803 0.876
F1-score
0.769 0.83
0.82
0.818 0.768 0.766 0.839 0.828 0.816 0.766 0.792 0.82
0.813 0.817 0.763 0.747 0.801 0.805 0.775 0.826
AUC
0.676 0.708 0.644 0.542 0.727 0.683 0.744 0.671 0.568 0.715 0.686 0.727 0.623 0.538 0.689 0.608 0.683 0.637 0.506 0.686
KC1
Precision
0.818 0.84
0.825 0.828 0.824 0.829 0.823 0.815 0.833 0.819 0.817 0.834 0.817 0.813 0.824 0.810 0.819 0.816 0.815 0.801
Recall
0.829 0.859 0.853 0.721 0.688 0.829 0.853 0.848 0.666 0.673 0.827 0.858 0.849 0.663 0.673 0.802 0.830 0.819 0.697 0.656
F1-score
0.822 0.827 0.82
0.752 0.728 0.818 0.814 0.813 0.709 0.715 0.821 0.827 0.818 0.694 0.716 0.805 0.810 0.813 0.751 0.701
AUC
0.742 0.807 0.782 0.782 0.771 0.742 0.805 0.779 0.776 0.747 0.743 0.812 0.784 0.767 0.757 0.715 0.785 0.763 0.764 0.799
KC2
Precision
0.876 0.879 0.871 0.879 0.878 0.87
0.879 0.87
0.878 0.874 0.882 0.877 0.87
0.879 0.879 0.866 0.863 0.866 0.872 0.870
Recall
0.859 0.922 0.914 0.904 0.789 0.854 0.924 0.913 0.897 0.779 0.868 0.924 0.909 0.897 0.786 0.817 0.884 0.857 0.879 0.769
F1-score
0.867 0.894 0.89
0.89
0.827 0.861 0.894 0.889 0.887 0.818 0.874 0.895 0.887 0.886 0.824 0.840 0.870 0.861 0.875 0.816
AUC
0.717 0.789 0.716 0.665 0.659 0.716 0.79
0.72
0.675 0.652 0.736 0.801 0.719 0.669 0.652 0.710 0.759 0.701 0.67
0.637
PC1
Precision
0.797 0.807 0.782 0.817 0.823 0.783 0.824 0.829 0.826 0.83
0.827 0.815 0.785 0.812 0.828 0.812 0.807 0.782 0.81
0.819
Recall
0.774 0.823 0.794 0.825 0.747 0.758 0.819 0.825 0.832 0.766 0.809 0.826 0.806 0.821 0.787 0.727 0.810 0.803 0.82
0.722
F1-score
0.782 0.811 0.785 0.815 0.768 0.767 0.818 0.824 0.822 0.784 0.815 0.816 0.792 0.81
0.798 0.767 0.808 0.792 0.814 0.767
AUC
0.75
0.787 0.735 0.815 0.815 0.747 0.805 0.783 0.826 0.819 0.806 0.808 0.754 0.781 0.812 0.770 0.767 0.737 0.74
0.809
JM1
Precision
0.747 0.742 0.732 0.756 0.757 0.76
0.76
0.757 0.767 0.761 0.76
0.764 0.764 0.767 0.745 0.738 0.747 0.742 0.756 0.740
Recall
0.778 0.757 0.762 0.777 0.593 0.787 0.806 0.803 0.793 0.725 0.784 0.8
0.801 0.803 0.604 0.766 0.760 0.777 0.785 0.511
F1-score
0.756 0.745 0.741 0.764 0.63
0.769 0.758 0.759 0.776 0.74
0.769 0.765 0.76
0.774 0.642 0.751 0.759 0.753 0.770 0.541
AUC
0.654 0.679 0.668 0.655 0.669 0.666 0.72
0.709 0.663 0.672 0.686 0.709 0.703 0.682 0.651 0.674 0.679 0.681 0.642 0.638
Average results
Precision
0.81
0.815 0.803 0.813 0.825 0.812 0.821 0.818 0.818 0.826 0.821 0.817 0.807 0.812 0.822 0.804 0.803 0.801 0.800 0.806
Recall
0.795 0.845 0.833 0.816 0.709 0.792 0.855 0.847 0.808 0.733 0.812 0.852 0.84
0.807 0.714 0.764 0.822 0.813 0.797 0.707
F1-score
0.799 0.821 0.811 0.808 0.744 0.796 0.825 0.823 0.802 0.765 0.814 0.825 0.814 0.796 0.749 0.782 0.810 0.805 0.797 0.730
AUC
0.708 0.754 0.709 0.692 0.728 0.711 0.773 0.732 0.702 0.721 0.731 0.771 0.717 0.687 0.712 0.695 0.735 0.704 0.664 0.714
FS: Feature Selection
Table 3. Comparison results of presented Wrapper feature selection techniques com-
bined with Vanilla GAN for all the used dataset (cont).
in GA and WOA method, and the lowest value is 0.732 for the JM1 dataset in
MA method. For the Recall measure, values almost higher than 0.80, PSO and
CS obtained the highest value of 0.924 for PC1 and the lowest value is 0.591 for
JM1 dataset in WOA method. For the F1-score, BBA reached the highest value
of 0.895 for the PC1 dataset, PSO and CS reached a value of 0.894, which is
also good, and the lowest value is 0.40 for the CM1 dataset. In terms of AUC
measure, for most of the cases, values are greater than 0.700 in CM1, PC1, KC1
and KC2. The highest value of AUC is 0.826 for KC2 in PSO method and the
lowest value is 0.509 for CM1. Additionally, the performance of the classiﬁers
based on wrapper feature selection methods was better than when no feature
selection methods are applied.
From the average results, it can be observed that PSO with Vanilla GAN
and Cuckoo Search with VanillaGAN signiﬁcantly produced highlighted values,
which are higher than others for most of the cases, followed by Mayﬂy Algorithm
with Vanilla GAN. Moreover, it is clear that the RF technique produces the best
performance for most cases among the used wrapper methods for evaluation
measures.
6
Conclusion
The performance of software fault prediction (SFP) is aﬀected by two ma-
jor factors that are high dimensional features and imbalanced classes. One of
the common ways to overcome these problem can be a hybrid feature selection
method combined with data sampling that generate balanced dataset with op-
timal features.


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
For the high dimension reduction, this paper presented six Wrapper methods
that are Genetic Algorithm, the Particle Swarm Optimization, Whale Optimiza-
tion Algorithm, Cuckoo Search, Mayﬂy Algorithm and Binary Bat Algorithm to
select important and relevant features from Promise dataset. Then the Vanilla
GAN was trained with the collected dataset to generate synthetic instances
of minority class to handle imbalanced data. Afterward, ﬁve machine learning
techniques were applied on balanced data in SFP. Experiment results show us
a signiﬁcant achievement of combination of wrapper feature selection and GAN
network for SFP, speciﬁcally the Particle Swarm Optimization with Vanilla GAN
and Cuckoo Search with VanillaGAN produced a good performance on most of
the dataset, followed by Mayﬂy Algorithm with Vanilla GAN.
In the future work, we intend to investigate on ensemble learning for feature
selection and several variations of GAN for handing the imbalanced dataset in
SFP.
References
1. Aggarwal, K., Singh, Y., Kaur, A., Malhotra, R.: Empirical study of object-oriented
metrics. J. Object Technol. 5(8), 149–173 (2006)
2. Arisholm, E., Briand, L.C., Johannessen, E.B.: A systematic and comprehensive
investigation of methods to build and evaluate fault prediction models. Journal of
Systems and Software 83(1), 2–17 (2010)
3. Brodzicki, A.; Piekarski, M.J.K.J.: The whale optimization algorithm approach for
deep neural networks. Sensors 21, 8003 (2021)
4. Caglayan, B., Tosun, A., Miranskyy, A., Bener, A., Ruﬀolo, N.: Usage of multiple
prediction models based on defect categories. In: Proceedings of the 6th Interna-
tional Conference on Predictive Models in Software Engineering. pp. 1–9 (2010)
5. Chandrashekar, G., Sahin, F.: A survey on feature selection methods. Computers
& Electrical Engineering 40(1), 16–28 (2014)
6. Colaco, S., Kumar, S., Tamang, A., Biju, V.G.: A review on feature selection
algorithms. Emerging Research in Computing, Information, Communication and
Applications: ERCICA 2018, Volume 2 pp. 133–153 (2019)
7. De Carvalho, A.B., Pozo, A., Vergilio, S.R.: A symbolic fault-prediction model
based on multiobjective particle swarm optimization. Journal of Systems and Soft-
ware 83(5), 868–882 (2010)
8. Elish, K.O., Elish, M.O.: Predicting defect-prone software modules using support
vector machines. Journal of Systems and Software 81(5), 649–660 (2008)
9. Gao, Z.M., Zhao, J., Li, S.R., Hu, Y.R.: The improved mayﬂy optimiza-
tion algorithm. Journal of Physics: Conference Series 1684, 012077 (11 2020).
https://doi.org/10.1088/1742-6596/1684/1/012077
10. Ghosh, M., Guha, R., Sarkar, R., Abraham, A.: A wrapper-ﬁlter feature selection
technique based on ant colony optimization. Neural Computing and Applications
32, 7839–7857 (2020)
11. Halstead, M.H.: Elements of Software Science (Operating and programming sys-
tems series). Elsevier Science Inc. (1977)
12. Khoshgoftaar, T.M., Gao, K., Napolitano, A.: An empirical study of feature rank-
ing techniques for software quality prediction. Int. J. Softw. Eng. Knowl. Eng. 22,
161–183 (2012)


---

A comparative study of Wrapper feature selection techniques in Software Fault Prediction
13. Laradji, I.H., Alshayeb, M., Ghouti, L.: Software defect prediction using ensemble
learning on selected features. Information and Software Technology 58, 388–402
(2015)
14. Lessmann, S., Baesens, B., Mues, C., Pietsch, S.: Benchmarking classiﬁcation mod-
els for software defect prediction: A proposed framework and novel ﬁndings. IEEE
transactions on software engineering 34(4), 485–496 (2008)
15. Malhotra, R.: A systematic review of machine learning techniques for software fault
prediction. Applied Soft Computing 27, 504–518 (2015)
16. McCabe, T.J.: A complexity measure. IEEE Transactions on software Engineering
(4), 308–320 (1976)
17. Meiliana, Karim, S., Warnars, H.L.H.S., Gaol, F.L., Abdurachman, E., Soewito,
B.: Software metrics for fault prediction using machine learning approaches: A
literature review with promise repository dataset. In: 2017 IEEE International
Conference on Cybernetics and Computational Intelligence (CyberneticsCom). pp.
19–23 (2017). https://doi.org/10.1109/CYBERNETICSCOM.2017.8311708
18. Moser, R., Pedrycz, W., Succi, G.: A comparative analysis of the eﬃciency of
change metrics and static code attributes for defect prediction. In: Proceedings of
the 30th international conference on Software engineering. pp. 181–190 (2008)
19. Moslehi, F., Haeri, A.: A novel hybrid wrapper–ﬁlter approach based on genetic
algorithm, particle swarm optimization for feature subset selection. Journal of Am-
bient Intelligence and Humanized Computing 11, 1105–1127 (2020)
20. Nakamura, R., Pereira, L., Costa, K., Rodrigues, D., Papa, J., Yang, X.S.:
Bba: A binary bat algorithm for feature selection. pp. 291 –297 (08 2012).
https://doi.org/10.1109/SIBGRAPI.2012.47
21. Ovat, F., Anyandi, A..J.: The particle swarm optimization (pso) algorithm ap-
plication – a review. Global Journal of Engineering and Technology Advances 3,
001–006 (06 2020)
22. Pandey, S.K., Mishra, R.B., Tripathi, A.K.: Machine learning based methods for
software fault prediction: A survey. Expert Systems with Applications 172, 114595
(2021)
23. Rathore, S.S., Chouhan, S.S., Jain, D.K., Vachhani, A.G.: Generative oversam-
pling methods for handling imbalanced data in software fault prediction. IEEE
Transactions on Reliability 71(2) (2022)
24. Shepperd, M., Song, Q., Sun, Z., Mair, C.: Data quality: Some comments on the
nasa software defect datasets. IEEE Transactions on Software Engineering 39(9),
1208–1215 (2013)
25. Turhan, B., Kocak, G., Bener, A.: Software defect prediction using call graph
based ranking (cgbr) framework. In: 2008 34th Euromicro Conference Software
Engineering and Advanced Applications. pp. 191–198. IEEE (2008)
26. Wang, F., Ai, J., Zou, Z.: A cluster-based hybrid feature selection method for de-
fect prediction. In: 2019 IEEE 19th International Conference on Software Quality,
Reliability and Security (QRS). pp. 1–9. IEEE (2019)
27. Wang, H., Khoshgoftaar, T.M., Napolitano, A.: Stability of ﬁlter-and wrapper-
based software metric selection techniques. In: Proceedings of the 2014 IEEE 15th
International Conference on Information Reuse and Integration (IEEE IRI 2014).
pp. 309–314. IEEE (2014)
28. Yang, X.S., Deb, S.: Cuckoo search via lévy ﬂights. In: 2009 World Congress on
Nature Biologically Inspired Computing (NaBIC). pp. 210–214 (2009)
29. Zervoudakis, K., Tsafarakis, S.: A mayﬂy optimization algorithm. Comput. Ind.
Eng. 145, 106559 (2020)
