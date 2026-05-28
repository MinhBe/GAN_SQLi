引用格式:罗艺铭,谭玉波,李建平.基于BERT-GAN 的SQL 注入攻击检测方法研究[J]. 微电子学与计算机,2024,41(11):39-
47.
LUO Y M,TAN Y B,LI J P. Research on SQL injection attacks detection method based on BERT-GAN[J]. Microelectronics &
Computer,2024,41(11):39-47.
DOI:10.19304/J.ISSN1000-7180.2023.0721
基于BERT-GAN 的SQL 注入攻击检测方法研究
罗艺铭,谭玉波,李建平
(河南工业大学 信息科学与工程学院, 河南 郑州 450001)
摘 要: 针对主流检测方法识别SQL 注入攻击面临的检测准确率不高和用于训练的大量真实数据集通常难以获
取的问题,提出了一种用于检测SQL 注入攻击的BERT-GAN 网络模型。通过半监督学习方案来综合对抗样本,
采用微调的BERT 模型处理未标记数据,利用生成对抗网络区分对抗性和真实示例以及检测恶意和良性样本。实
验结果表明,模型在公开管理和标准化数据集sqli,sqliv2 和自建的sqli-extend 数据集上与基于CNN、LSTM、BERT-
Base、GAN-Base 模型的SQL 注入攻击检测方法对比,准确率、精确率、召回率和F1 值均有一定程度提高。模型的
目标损失函数收敛速度更快说明所提模型具有高效性。
关键词: SQL 注入;攻击检测;生成对抗网络;BERT;半监督学习
中图分类号: TP393 文献标识码: A 文章编号: 1000-7180(2024)11-0039-09
Research on SQL injection attacks detection method based on BERT-GAN
LUO Yiming,TAN Yubo,LI Jianping
(College of Information science and Engineering, He'nan University of Technology, Zhengzhou 450001, China)
Abstract:A BERT-GAN network model for detecting SQL injection attacks is proposed to solve the problems faced by
the mainstream detection methods, such as low detection accuracy and difficult to obtain a large number of real data sets for
training. The confrontation samples are synthesized by a Semi-Supervised Learning scheme.The unmarked data is processed
using the fine-tuning of BERT-like architectures.Adversarial and real examples as well as detecting malicious and benign
samples are distinguished by generating confrontation settings. The experimental results demonstrate that the accuracy,
precision, recall and F1 score of the proposed model have been enhanced to a certain degree on openly managed and
standardized datasets such as sqli, sqliv2 and self-built sqli-extend datasets. These improvements are observed in
comparison to SQL injection detection methods based on CNN, LSTM, BERT-Base, and GAN-Base models. Furthermore,
the faster convergence rate of the target loss function indicates that the proposed model exhibits high efficiency.
Key words:SQL injection;attacks detection;generative adversarial network;BERT;semi-supervised learning

1 引言
近年来,随着移动互联网、物联网、5G 通信
等技术的快速发展,互联网与各行各业跨界融合。
不仅在消费及政企领域,网约车、网络支付、网络
购物、网络娱乐、网络新闻、在线办公、在线政务
等新兴应用改变了人们的生活和工作方式。而且在
生产及物流领域,5G+工业互联网形成了人、机、


收稿日期: 2023-09-13; 修回日期: 2023-11-12
基金项目:国家自然科学基金(62276091)

第 41 卷 第 11 期
微 电 子 学 与 计 算 机 https://www.journalmc.com
Vol. 41 No. 11
2024 年 11 月
MICROELECTRONICS & COMPUTER
November 2024
https://www.journalmc.com


---

物全面连接的新型生产方式,正在向航空航天、石
化化工、建材、港口、纺织、家电等垂直领域加速
延伸。支撑这些互联网应用及关键信息基础设施正
常运转的重要组件之一就是类型各异、分散部署的
数据库,储存着珍贵的行业数据及敏感的个人信息。
由于这些数据对网络黑色产业链有重大价值,因此
数据库一直是黑客攻击的重要目标。
2022 年3 月,NVIDIA 内部1TB 的敏感文件遭
窃,7 万员工信息泄露。同年11 月,社交软件脸书
(Facebook)被爱尔兰数据保护委员会因约5.33 亿用
户的个人数据被黑客窃取泄露,处以2.65 亿欧元
(合约20 亿人民币)的罚款。据统计,2022 年将近
20% 的中国网民遭遇过个人信息泄露事件
[1],在数
据安全领域,SQL 注入攻击一直是主要的威胁类型。
2020 年被确认的266 个数据库系统漏洞中,
MySQL 漏洞占据总漏洞数量的一半以上
[2]。此外,
在开源Web 应用程序安全项目 (Open Web Application Security Project, OWASP)中公布的10 个最常
见的应用程序漏洞中
[3],SQL 注入攻击的风险排在
第一位。因此,研究和防范SQL 注入攻击是一项必
要的安全任务。在此基础上,本文提出了一种基于
BERT-GAN 的SQL 注入攻击检测模型,以帮助软
件开发人员及时发现网络中可能存在的SQL 注入漏
洞,从而确保信息网络的安全。

2 研究背景

2.1 SQL 注入攻击原理
SQL 注入的概念第一次被提出在是1998 年
《Phrack》第54 期中的"NT Web Technology Vulnerabilities"文献里
[4],SQL 注入攻击的流程如图1
所示。攻击者不需要获取管理员的用户名和密码,
直接执行恶意SQL 命令欺骗服务器以访问资源,或
通过插入、修改以及删除数据篡改数据库
[5-8],导致
整个数据库的丢失或损坏。


浏览器
Web 服务器
数据库
SQL
注入攻击
选择查询
返回错误信息
返回数据
图1 SQL 注入攻击原理图
Fig. 1 Schematic diagram of SQL injection attack

新型的攻击与以往有很大不同,它可能会攻击
任何带有漏洞的动态ASP 页面,尤其是一些旧网
站
[9],攻击者可以使用HDSI、HBSI 等SQL 注入工
具直接攻击网站。这些工具的使用门槛很低,攻击
者很容易取得服务器的控制权,相应的防范难度和
造成的危害也提高了。

2.2 基于机器学习的注入攻击检测算法
机器学习检测算法通过提供的大量数据进行分
析并训练模型,具有灵活性和伸缩性
[10]。针对过多
的文本特征会产生"维灾难"及文本的训练和分类
时间过长等问题,文献[11] 使用支持向量机
(Support Vector Machine, SVM)作为分类器,提高
了检测SQL 注入攻击的召回率,降低了训练和分类
的时间开销。考虑到识别攻击的难度和成本,文
献[12] 使用了一种融合特征选择的随机森林(Random Forest, RF)的攻击检测方法,该方法集成了一
系列用于检测SQL 注入攻击的功能,通过分析
Web 访问日志来提取SQL 注入攻击特征,对异常
流量样本进行降维,将特征选择算法嵌入随机森林
的单个基学习器,提高了模型精度,然而这种方法
的准确性还有待提高。
为了进一步提升机器学习检测算法的性能,深
度学习检测算法学习了大量代表攻击或正常的历史
数据,识别攻击模式和了解检测到的流量,最终实
现在攻击发生之前预测将要产生的攻击。文献[13]
提出使用卷积神经网络(Convolutional Neural
Network, CNN)来检测PHP 代码中的SQL 注入漏洞,
通过定制预处理阶段来去除不必要的数据,添加语
义标签作为补充因素来提高训练效率。文献[14] 提
出一种基于长短期记忆网络(Long Short-Term Memory, LSTM)的SQL 注入攻击检测方法,生成有效的
正样本,解决了由于缺乏正样本而导致的过拟合问
题。但这些模型无法应对真实网络攻击的复杂环境,
尤其是存在对文本深层语义和挖掘上下文关联信息
方面的短板。

2.3 基于生成对抗网络的攻击检测算法
上述大多数的SQL 注入攻击检测算法过于强
调防御措施且难以识别新的攻击。传统的杀毒软件
用病毒库的方式,只能应付库中已存的病毒,往往
无法识别新产生的攻击,更何况要制定出相应的防
御策略。因此不能仅依靠挖掘现有的攻击报文来实
现攻击检测,而是要学习攻击者的理性决策过程,
尝试使用博弈的方式来理解攻击者和防御者之间的
对抗。
生成对抗网络 (Generative Adversarial Network,
GAN)
[15] 可以从文本中提取和学习细粒度信息,并
使用生成器创建合成示例,同时利用鉴别器来区分
40
微电子学与计算机
2024 年
https://www.journalmc.com


---

真实示例和合成示例,从而使生成器和鉴别器互相
对抗、共同进化。Yin 等
[16] 介绍了鉴别器并提出了
一个基于改进GAN 的网络检测的框架,以扩大标
签的数量,实现僵尸网络的识别和分类。Lee 等
[17]
提出一种使用GAN 创建相似攻击流量的方法,解
决真实网络攻击数据集的样本不平衡问题,通过增
强数据集来提高攻击检测的准确率。Lu 等
[18] 通过
将深度卷积GAN 与遗传算法相结合,在现有不同
类型的SQL 注入攻击样本的基础上生成新样本,增
加已知攻击样本的数目来缓解模型的过拟合。但这
些方法依赖先验知识的积累和生成的样本质量,难
以解决缺乏先验知识的新型SQL 注入攻击类型的样
本标签少的问题。
针对上述问题,本文继承了传统的SQL 注入
攻击检测算法的思想,试图采用深度学习方法,通
过结合GAN 模型博弈原理和基于上下文的BERT
模型,针对SQL 注入攻击检测不能及时检测到新
的SQL 注入攻击的问题,提出了基于BERT-GAN
的SQL 注入攻击检测模型。

3 基于BERT-GAN 的SQL 注入攻击检测
算法

3.1 算法模型整体架构
为了解决SQL 注入攻击检测框架需要根据已
知数据构建词库,采用语法解析、词嵌入编码可能
隐藏SQL 注入关键特征等问题,本文提出基于
BERT-GAN 的SQL 注入攻击检测模型,如图2 所
示。该模型使用基于上下文的BERT 模型,提供高
层次的样本特征向量,突出不同样本之间的差异;
同时为了实现特征的有效性并保持模型的泛化能力,
提出改进的半监督条件GAN 模型,生成器生成一
组给定随机分布的假示例向量,与未标记和标记样
本经由BERT 模型提取的特征向量分别作为鉴别器
的输入,利用对抗训练不断强化鉴别器,与此同时,
使用标记的数据来训练鉴别器进行分类,从而提高
模型的整体质量。该模型包括两个模块:数据特征
学习和异常检测。


数据特征学习模块
嵌入
无标签
有标签
编码器 1
编码器 2
BERT
编码器
解码器
生成器
鉴别器
真实
虚假
0
1
异常检测模块
随机噪声
编码器 N
图2 BERT-GAN 网络模型架构图
Fig. 2 BERT-GAN network model architecture diagram


3.2 数据特征学习
在实际场景中,大多数的基准测试都是在包含
数万个样本的数据集上实现的。然而,获得高质量
的注释数据是相当昂贵且耗时,相比之下,描述目
标任务特征的未标记示例通常较容易获取。而基于
Transformer 架构的双向编码器表示(Bidirectional
Encoder Representations from Transformers, BERT)是
基于上下文的嵌入模型
[19],有多层网络,每层包含
几个能够进行非线性变换的神经元,具有较强的非
线性拟合能力。为了减少对标注样例的需求,本文
的数据特征学习模块使用BERT 模型学习原始样本
的上下文表示,为异常检测模块提供高层次的样本
特征向量。
BERT 模型的核心由多个Transformer 编码器组
成,与传统的单向语言模型或者多个浅层拼接后的
单向语言模型相比, BERT 能够学到更重要的单词
或句子语义以及文本中不同级别的关系特征
[20],同
时使用上亿级别的无标注语料进行预训练,能够生
成更加准确、更通用的词向量或者句向量表示
[21]。
很多下游任务可以通过在预训练模型的基础上添加
第 11 期
罗艺铭,等:基于BERT-GAN 的SQL 注入攻击检测方法研究
41

https://www.journalmc.com


---

一个额外的输出层进行微调来实现较好的任务性能。
单个Transformer 编码器由多头注意力机制和前馈
网络层组成,是一种迁移学习,基于Transformer
架构和注意力机制
[22],BERT 模型的架构如图3 所示。

编码器 2
编码器 N
叠加和归一组件
多头注意力层
前馈网络层
叠加和归一组件
R1
R2
R3
R4 ...
编
码
器
1
Rn
图3 BERT 模型图
Fig. 3 BERT model diagram

BERT 模型在巨大规模语料库上基于下句预测
(Next Sentence Prediction, NSP)和掩码语言模型
(Masked Language Model, MLM)两个任务进行预训
练。NSP 的任务是判断给定的两个句子是否是连续
的,能够让模型学习到连续文本之间的关系,使模
型具备长距离语义捕捉能力。MLM 类似于完形填
空,将一些词打上掩码,用剩余词去预测打上掩码
的词,具体做法是随机遮掩15% 的单词,这些单词
中的10% 随机替换成其他单词,10% 保持不变,
80% 替换成掩码[MASK],MLM 能够使模型
学习到深度的双向信息,具有更强的多义性学习
能力。
在将数据输入BERT 之前,首先使用3 层嵌入
层将输入转换为嵌入,如图4 所示,3 层嵌入层分
别为标记嵌入层、分段嵌入层及位置嵌入层。其中,
标记嵌入层在第一句的开头加上一个特殊的标记
[CLS] 用于分类任务,其在最后一个隐藏层的隐藏
状态代表整个序列的聚合表示,在句尾添加句子分
隔标记[SEP] 表示句子的结束。分段嵌入层只用输
出嵌入EA 或者EB 用来区分给定的句子,如果输
入的标记属于句子A,那么该标记将被映射到嵌入
EA,同理,如果输入的标记属于句子B,那么该标
记将被映射到嵌入EB。位置嵌入层给出了每个标
记在句子中的位置嵌入,由于Transformer 没有任
何循环机制,是以并行方式处理所有词的,因此在
直接向BERT 输入词之前,需要给出标记在句子中
的位置信息。


[CLS]
Input
union
select
[SEP]
##or
user
like
[SEP]
E[CLS]
标记嵌入层
Eunion
Eselect
E[SEP]
E##or
Euser
Elike
E[SEP]
EA
EA
EA
EA
分段嵌入层
位置嵌入层
EB
EB
EB
EB
E0
E1
E2
E3
E4
E5
E6
E7
图4 嵌入层图
Fig. 4 Embedding layer diagram


3.3 异常检测模块
异常检测模块通过生成器生成的伪样本和带有
标签的真实样本,帮助鉴别器去学习数据中的相关
模式,训练结束后,丢弃生成器,保留原始模型的
其余部分实现SQL 注入攻击检测任务。训练GAN
就是在一个双人非合作博弈中找到纳什均衡,生成
器生成伪样本,然后将伪样本和真实样本都输入鉴
别器,鉴别器再判断其是真或假。传统的生成对抗
网络由生成器G 和鉴别器D 组成,GAN 的目标函
数为
min
G max
D V(D,G) =Ex∼Pr[lgD(x)]
+ Esim∼Pz[lg(1−D(G(sim)))] (1)
式中:E 为真实数据和噪声数据的数学期望;Pr 为
生成器G 在真实数据上的分布;D(x)为鉴别器试图
判断样本是否为真实样本的概率,输入G 网络的噪
42
微电子学与计算机
2024 年
https://www.journalmc.com


---

声变量用z 表示;Pz 为输入噪声变量的分布
(如均匀分布、正态分布或高斯分布);G(z)表示生
成器接收一个随机噪声z 后生成的伪数据。原始
GAN 的生成器G 只能根据输入的随机噪声生成数
据,生成的结果不可控,基于简单GAN 的方式训
练的表现不是很好。故而针对此类问题,将半监督
学习引入到生成对抗网络中,构造一种半监督条件
生成对抗网络,可以充分的利用无标签数据辅助有
监督学习的训练。
半监督条件生成对抗网络的鉴别器接收3 种输
入:生成器生成的伪样本x*、训练数据集中无标签
的真实样本x 和有标签的真实样本(x, y),其中y 表
示给定样本x 的标签。对于有标签的真实样本(x, y),
输入鉴别器后,进行正确的分类。对于无标签的真
实数据x,只需训练它被判定为真即可。对于生成
器的伪样本x*,鉴别器则希望能正确的将其判定为
假,但生成器却希望鉴别器能将其判定为真,由此
产生了对抗。训练的目的是使该网络成为仅使用小
部分标签数据的半监督分类器,其准确率尽可能接
近全监督分类器。生成器的目的是通过提供附加信
息(生成的伪数据)来帮助鉴别器去学习数据中的相
关模式,从而提高其分类准确率,训练结束时,生
成器将被丢弃,而训练有素的鉴别器将被用作分
类器。
半监督条件生成对抗网络的目标函数为
Ladv(G,D) =Ex,y[(D(x,y)−1)2]
+Ex,y[(D(G(x,ζ,y),y)+1))2]
(2)
生成器G 尝试使生成的数据和真实数据之间的
差异最小化;鉴别器D 试图通过尽可能准确地识别
真实数据和G 伪造的数据来最大化这一点。
本文先用真实样本x 训练鉴别器,再用生成的
虚假样本G(x, ζ, y)训练,在训练数据上批量训练鉴
别器D,不停地迭代后再训练G,同时保持鉴别器
的权重不变。然后,使用交叉熵区分良性和恶意样
本,表达式为
Lclass (D) = −
k∑
i=0
yi lg(y′
i
)
(3)
生成器还包含重构损失,表达式为
Lrec(G) = Ex,y∥G(x,ζ,y)−x∥2
(4)
使用生成器将初始样本转换为目标域的样本,
然后从转换后的样本基础上重建原始样本,最后比
较原始样本和重构样本的正则化距离,合并损失使
生成的样本与真实的样本一致。
结合式(2)和式(3),目标函数最终表述为
min
G,D (max
D (λadvLadv(D))+λrec [Lrec (G)]
+λclass [Lclass (D)])
(5)
损失加权决定了在训练时优先考虑哪个架构,
为了更好的分类预测,分配更多权重。
生成器将噪声向量作为输入,以创建良性或恶
意的虚假样本。噪声矢量在输入前由高斯滤波器进
行平滑处理。生成器由常规卷积、转置卷积、批量
归一化和Leaky-ReLU 激活层组成。其中,编码器
由5 个卷积层组成,特征数为[32, 64, 128, 512,
1 024],解码器由5 个转置卷积层组成,特征数为
[1 024, 512, 128, 64, 32],最后使用Sigmoid 函数激
活并输出与真实样本维度相同的虚假样本。
鉴别器依次接收经由BERT 模型处理后的真实
样本和虚假样本作为输入,同时,它还预测输入是
真实还是虚假,并且将其分类为良性或恶意。鉴别
器由卷积层、批处理归一化层、Leaky-ReLU 激活
层和全连接层组成。其中,编码器由6 个卷积层和
2 个密集层组成,特征数为[16, 16, 32, 32, 64, 64,
128, 64]。最后,使用两种激活函数:①使用
Sigmoid 激活函数区分真实或虚假样本,②使用
Softmax 激活函数在给定数量的类别上的概率分布
来区分良性或恶意类样本,其中的每一个概率代表
了该样本属于某类的概率,给一个给定类别标签分
配的概率越高,鉴别器就越确信该样本属于这一给
定的类。
训练过程尝试优化两个竞争损失,即生成器的
损失LG 和鉴别器的损失LD。在反向传播过程中,
只有当其被错误地归类时,才会被考虑在损失计算
中。在所有其他情况下,其对损失的贡献被掩盖,
因此,标记的例子有助于监督损失。生成器生成的
样例对LD 和LG 都有影响,如果找不到生成器生
成的样例,鉴别器就会被扣分,反之亦然。在更新
鉴别器时,同时考虑标记和未标记的数据并且更改
BERT 权重以微调其内部表示。训练结束后,丢弃
生成器,保留原始模型的其余部分进行检测任务的
预测。

4 实验过程与评估

4.1 实验数据预处理
将模型在Kaggle 中提供的公开管理和标准化数
据集sqli 和sqliv2 上进行对比实验,该模型由从各
种来源收集的良性语句和SQL 注入攻击语句组成。
第 11 期
罗艺铭,等:基于BERT-GAN 的SQL 注入攻击检测方法研究
43

https://www.journalmc.com


---

但是,仅仅使用公开数据集会有注入类型样本不全
面或稀少、不同数据库语法差异及未能包括全部种
类的SQL 注入攻击等问题,使得数据清洗及人工处
理变得非常困难。故而,为了使本文所使用的数据
集更全面且实用性强,收集了以下两类 SQL 注入攻
击样本作为补充数据使用:①通过自动注入工具
SQLMAP
[14] 和WEB 应用环境DVWA
[23] 手动捕获
网络流量,并通过修改Sqlmap 脚本tamper 的方式
丰富SQL 注入攻击;②通过河南工业大学信息化管
理中心安全感知平台提供的实时SQL 注入漏洞数据,
将二者合并为sqli-extend 数据集。
通过采集获得的原始样本并不能直接用于后续
步骤输入,存在一些相似无用的冗余特征,因此需
要对样本进行必要的预处理操作,如图5 所示。


公开数据集
sqli-extend
数据集
合并数据
标注正常样本
标注攻击样本
原始数据集
核对样本标签
数据采集模块
筛选重复样本
统一关键词
删除敏感信息
数据清洗模块
图5 数据预处理图
Fig. 5 Data preprocessing diagram

数据清洗包括筛选十分相似或者重复的样本、
甄别和去除标注为异常的原始样本中可能包含的个
别正常样本,统一特定字段的关键词大小写,修正
表名、查询内容等字段以及删除异常样本中包含的
网站账号信息等。对原始样本进行清洗、融合等操
作后得到规范可用的实验数据,最终实验样本集的
具体信息如表1 所示。


表 1 样本集分布
Tab. 1 Sample set distribution
数据集
sqli
sqliv2
sqli-extend
总样本集
4 200
33 761
109 518
训练集
3 360
27 009
87 615
测试集
840
6 752
21 903


4.2 实验环境及参数设置
采用Python 3.7 编程语言,在Windows10 操作
系统,Intel(R) Core(TM) i7-10 700 CPU @
2.90 GHz 处理器和NVIDIA GeForce RTX 3 090 上
训练本文模型。将批量大小设置为64,引入
Dropout 层随机丢弃神经元提高网络的稳定性,使
用Adam 优化器
[24] 对模型中的网络进行优化。

4.3 实验结果及分析
收集并整理了SQL 注入攻击检测领域近3 年
的研究成果,分别采用基于CNN
[25]、LSTM
[26]、
BERT-Base
[27] 和GAN-Base
[28] 模型的SQL 注入攻击
检测方法与本文所提模型在公开管理和标准化数据
集sqli 和sqliv2 和自主构建的sqli-extend 数据集上
对比评估效果,验证本文模型的性能。实验结果使
用准确率(Accuracy, 记为Acc)、精确率(Precision, 记
为P)、召回率(Recall, 记为Rcc)和F1 分数来综合评
估模型的异常检测性能,4 个评估指标的计算公式
分别为
Acc =
TN +TP
TN +TP+ FN + FP
(6)
P =
TP
TP+ FP
(7)
R =
TP
TP+ FN
(8)
F1 = 2PR
P+R
(9)
准确率指预测正确的样本数在样本总数中所占
比例,从准确率指标来看,本文模型的平均准确率
最高如图6 所示,约为94.67%,比CNN 约高6.4%,
比LSTM 约高4.45%,比GAN-Base 约高1.45%,
比BERT-Base 约高2.04%。


0
20
40
60
80
100
0.80
0.85
0.90
0.95
1.00
Accuracy
Epoch
CNN
LSTM
GAN-Base
BERT-Base
BERT-GAN
图6 各模型准确率对比图
Fig. 6 Comparison chart of accuracy of various models

在保证精确率的条件下,提升SQL 注入攻击
检测任务的召回率和F1 分数。其中,模型的对比
结果以及性能指标如图7 所示。
从精确率指标来看,本文模型的平均精确率最
高,约为95.18%,比CNN 约高2.76%,比LSTM
约高1.97%,比GAN-Base 约高0.66%,比BERT-
44
微电子学与计算机
2024 年
https://www.journalmc.com


---

Base 约高1.4%。本文模型识别sqli-extend 的SQL
注入攻击序列中精确率达到97.19%。


0.5
0.6
0.7
0.8
0.9
1.0
sqli
sqliv2
(a) 精确率对比图
(a) Precision comparison chart
(b) 召回率对比图
(b) Recall rate comparison chart
sqli-extend
Precision
CNN
LSTM
GAN-Base
BERT-Base
BERT-GAN
0.5
0.6
0.7
0.8
0.9
1.0
sqli
sqliv2
sqli-extend
Recall
CNN
LSTM
GAN-Base
BERT-Base
BERT-GAN
0.5
0.7
0.9
0.8
0.6
1.0
sqli
sqliv2
sqli-extend
F1
CNN
LSTM
GAN-Base
BERT-Base
BERT-GAN
(c) F1 分数对比图
(c) F1 score comparison chart
图7 各检测模型性能对比图
Fig. 7 Performance comparison of each detection model

从召回率指标来看,本文模型的平均召回率最
高,约为96.12%,比CNN 约高3.74%,比LSTM
约高1.43%,比GAN-Base 约高0.64%,比BERT-
Base 约高1.03%。本文模型识别sqli-extend 的SQL
注入攻击序列中召回率达到97.79%。
从F1 分数指标来看,本文模型的平均F1 分数
最高,约为95.65%,比CNN 约高3.25%,比
LSTM 约高1.68%,比GAN-Base 约高0.66%,比
BERT-Base 约高1.23%。本文模型识别sqli-extend
的SQL 注入攻击序列中F1 分数达到97.49%。
以上实验结果表明,本文模型在SQL 注入攻
击检测任务中取得了较好的效果,在数据集上的平
均精确率、召回率和F1 值分别为0.951 8、0.961 2
和0.956 5,比其余模型都有一定程度的提高。本文
模型运用大量真实环境下的无标注数据来扩充深度
学习知识库,从而大大降低了对于难以获取的标注
数据的需求,进而提高了模型的性能,说明了本文
所提模型对于实现检测SQL 注入攻击任务的高效性。
本文所提模型和对比模型的目标损失函数值随
着网络迭代次数的变化如图8 所示,随着迭代轮数
的不断增加,在训练到第700 轮时,目标损失函数
值的下降相对稳定,有效避免了网络的梯度爆炸,
使得BERT-GAN 网络的异常检测性能更加稳定。
在同样的迭代次数下,本文所提方法的Loss 最低,
在同样Loss 的情况下,本文所提方法的迭代次数最
少,特别是Loss 降低至0.2 以下时,Epoch 差距明
显,由此可得,经过多轮训练本文所提模型可以稳
定高效的检测出SQL 注入攻击数据。


0
200
400
600
800
1 000
0
0.2
0.4
0.6
0.8
Loss
Epoch
BERT-GAN
CNN
LSTM
GAN-Base
BERT-Base
图8 训练损失变化曲线图
Fig. 8 Training loss variation graph


5 结束语
针对传统检测模型正确率不高和获取真实攻击
数据代价高昂的问题进行研究,提出了一种通过半
监督学习方案来综合对抗样本的BERT-GAN 模型。
首先提取输入数据的标注和无标注信息,然后将其
融合到BERT 模型的特征向量中,使得最终的融合
向量包含了足够多的先验知识,同时合成对抗示例
并预测它们的类别,最终实现SQL 注入攻击检测。
实验结果表明,提出的BERT-GAN 模型相比于其
他多个对比模型,能够有效利用无标注数据降低模
型对难以获取的标注数据的依赖程度,并且拥有较
高的检测准确率。在今后的研究中,可以采用其他
架构或尝试在本地客户端和全局服务器端上实时检
第 11 期
罗艺铭,等:基于BERT-GAN 的SQL 注入攻击检测方法研究
45

https://www.journalmc.com


---

测SQL 注入攻击。
参考文献:
 中国互联网络信息中心. CNNIC 发布第51 次《中国
互联网络发展状况统计报告》[EB/OL]. https://cnnic.
cn/n4/2023/0302/c199-10755.html, 2023.
CNNIC. Statistical report on the development of internet
in China[EB/OL]. https://cnnic.cn/n4/2023/0302/c199-
10755.html, 2023.
[1]
 国家计算机网络应急技术处理协调中心. 2020 年中
国互联网网络安全报告[R]. 北京: 人民邮电出版社,
2020.
CNCERT. China internet network security report[R].
Beijing: Posts & Telecom Press, 2020.
[2]
 OWASP. Top 10 web application security risks[EB/OL].
https://www.owasp.org/index.php/Category:
OWASP_Top_Ten_Project, 2023.
[3]
 RFP. NT web technology vulnerabilities[EB/OL]. http://
phrack.org/issues/54/8.html, 2023.
[4]
 SINGH N, DAYAL M, RAW R S, et al. SQL injection:
types, methodology, attack queries and prevention[C]//
Proceedings of the 3rd International Conference on Computing for Sustainable Global Development. Piscataway:
IEEE, 2016: 2872-2876.
[5]
 ABIRAMI J, DEVAKUNCHARI R, VALLIYAMMAI
C. A top web security vulnerability SQL injection attacksurvey[C]// Proceedings of 2015 Seventh International
Conference on Advanced Computing (ICoAC). Piscataway: IEEE, 2015: 1-9. DOI: 10.1109/ICoAC.2015.
7562806.
[6]
 QIAN L, ZHU Z Y, HU J, et al. Research of SQL injection attack and prevention technology[C]//Proceedings of
2015 International Conference on Estimation, Detection
and Information Fusion (ICEDIF). Piscataway: IEEE,
2015: 303-306. DOI: 10.1109/ICEDIF.2015.7280212.
[7]
 KUMAR P, PATERIYA R K. A survey on SQL injection attacks, detection and prevention techniques[C]//
Proceedings of 2012 Third International Conference on
Computing, Communication and Networking Technologies. Piscataway: IEEE, 2012: 1-5. DOI: 10.1109/IC-
CCNT.2012.6396096.
[8]
 王安琪, 杨蓓, 张建辉, 等. SQL 注入攻击检测与防御
技术研究综述[J]. 信息安全研究, 2023, 9(5): 412-
422. DOI: 10.12379/j.issn.2096-1057.2023.05.02.
WANG A Q, YANG B, ZHANG J H, et al. A survey of
SQL
 injection
 attack
 detection
 and
 defense
technology[J]. Journal of Information Security Research,
2023, 9(5): 412-422. DOI: 10.12379/j.issn.2096-1057.
2023.05.02.
[9]
 黄小丹. SQL 注入漏洞检测技术综述[J]. 现代计算
机, 2020(10): 51-58. DOI: 10.3969/j.issn.1007-1423.
[10]
2020.10.011.
HUANG X D. Survey of SQL injection vulnerability detection[J]. Modern Computer, 2020(10): 51-58. DOI: 10.
3969/j.issn.1007-1423.2020.10.011.
 HASAN M, BALBAHAITH Z, TARIQUE M. Detection
of SQL injection attacks: A machine learning approach[C]// Proceedings of 2019 International Conference on
Electrical and Computing Technologies and Applications
(ICECTA). Piscataway: IEEE, 2019: 1-6. DOI: 10.1109/
ICECTA48151.2019.8959617.
[11]
 UWAGBOLE S O, BUCHANAN W J, FAN L. An applied pattern-driven corpus to predictive analytics in mitigating SQL injection attack[C]// Proceedings of the
2017 Seventh International Conference on Emerging Security Technologies (EST). Piscataway: IEEE, 2017: 12-
17. DOI: 10.1109/EST.2017.8090392.
[12]
 ZHANG K, DATASET A T. A machine learning based
approach to identify SQL injection vulnerabilities[C]//
Proceedings of 2019 34th IEEE/ACM International Conference on Automated Software Engineering (ASE). Piscataway: IEEE, 2019: 1286-1288. DOI: 10.1109/ASE.
2019.00164.
[13]
 LI Q, WANG F, WANG J F, et al. LSTM-based SQL injection detection method for intelligent transportation system[J]. IEEE Transactions on Vehicular Technology,
2019, 68(5): 4182-4191. DOI: 10.1109/TVT.2019.
2893675.
[14]
 GOODFELLOW I, POUGET-ABADIE J, MIRZA M, et
al. Generative adversarial nets[J]. Communications of
the ACM, 2020, 63(11): 139-144. DOI: 10.1145/
3422622.
[15]
 YIN C L, ZHU Y F, LIU S L, et al. An enhancing framework for botnet detection using generative adversarial
networks[C]// Proceedings of 2018 International Conference on Artificial Intelligence and Big Data (ICAIBD).
Piscataway: IEEE, 2018: 228-234. DOI: 10.1109/ICAIBD.
2018.8396200.
[16]
 LEE W H, LIM C S, NOH B N. Generation of similar
traffic using GAN for resolving data imbalance[C]// Proceedings of the CSA-CUTE 2018 on Advances in Computer Science and Ubiquitous Computing. Heidelberg:
Springer, 2018: 1-7. DOI: 10.1007/978-981-13-9341-9_1.
[17]
 LU D, FEI J L, LIU L, et al. A GAN-based method for
generating SQL injection attack samples[C]// Proceedings of 2022 IEEE 10th Joint International Information
Technology and Artificial Intelligence Conference (ITA-
IC). Piscataway: IEEE, 2022: 1827-1833. DOI: 10.1109/
ITAIC54216.2022.9836726.
[18]
 DEVLIN J, CHANG M W, LEE K, et al. Bert: pre-training of deep bidirectional transformers for language understanding[J]. Computation and Language, 2018, 23(2): 3-
19.
[19]
46
微电子学与计算机
2024 年
https://www.journalmc.com


---

 林孟达, 李书豪. 融合BERT 嵌入与注意力机制的方
面情感分析[J]. 现代电子技术, 2022, 45(12): 130-
136. DOI: 10.16652/j.issn.1004-373x.2022.12.024.
LIN M D, LI S H. Aspect sentiment analysis integrating
BERT embedding and attention mechanism[J]. Modern
Electronics Technique, 2022, 45(12): 130-136. DOI: 10.
16652/j.issn.1004-373x.2022.12.024.
[20]
 邓维斌, 朱坤, 李云波, 等. FMNN: 融合多神经网络的
文本分类模型[J]. 计算机科学, 2022, 49(3): 281-287.
DOI: 10.11896/jsjkx.210200090.
DENG W B, ZHU K, LI Y B, et al. FMNN: text classification model fused with multiple neural networks[J].
Computer Science, 2022, 49(3): 281-287. DOI: 10.
11896/jsjkx.210200090.
[21]
 SCHUSTER M, NAKAJIMA K. Japanese and Korean
voice search[C]//Proceedings of 2012 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). Piscataway: IEEE, 2012: 5149-5152.
DOI: 10.1109/ICASSP.2012.6289079.
[22]
 DURAI K N, SUBHA R, HALDORAI A. A novel method to detect and prevent SQLIA using ontology to cloud
web security[J]. Wireless Personal Communications,
2021, 117(4): 2995-3014. DOI: 10.1007/s11277-020-
07243-z.
[23]
 KINGMA D P, BA J. Adam: a method for stochastic optimization[C]//Proceedings of the 3rd International Conference for Learning Representations. San Diego: ICLR,
2015.
[24]
 洪正. 基于机器学习的SQL 注入和XSS 攻击检测技
术研究[D]. 南昌: 南昌大学, 2022. DOI: 10.27232/d.
[25]
cnki.gnchu.2022.002909.
HONG Z. Research on SQL injection and XSS attack detection technology based on machine learning[D]. Nanchang: Nanchang University, 2022. DOI: 10.27232/d.cnki.
gnchu.2022.002909.
 邱超. 基于深度学习的SQL 注入攻击分类方法研究
与应用[D]. 南昌: 南昌大学, 2022. DOI: 10.27232/d.
cnki.gnchu.2022.002068.
QIU C. Research and application of SQL injection attack
classification method based on deep learning[D]. Nanchang: Nanchang University, 2022. DOI: 10.27232/d.cnki.
gnchu.2022.002068.
[26]
 曹晓斌. 基于深度学习的SQL 注入检测研究[D]. 南
宁: 广西大学, 2020. DOI: 10.27034/d.cnki.ggxiu.2020.
001596.
CAO X B. Research on SQL injection detection based on
deep learning[D]. Nanning: Guangxi University, 2020.
DOI: 10.27034/d.cnki.ggxiu.2020.001596.
[27]
 张星. 基于GAN 的SQL 注入漏洞挖掘技术[D]. 西
安: 西安电子科技大学, 2021. DOI: 10.27389/dcnki.
gxadu.2021.000258.
ZHANG X. The technology of SQL injection vulnerability mining based on GAN[D]. Xi'an: Xi'an University of
Electronic Science and Technology, 2021. DOI: 10.27389/
dcnki.gxadu.2021.000258.
[28]
作者简介:
罗艺铭 硕士研究生,aliceluoym@163.com
谭玉波(通信作者) 博士,副教授,benentan@163.com
第 11 期
罗艺铭,等:基于BERT-GAN 的SQL 注入攻击检测方法研究
47

https://www.journalmc.com
