PrivacyLens — Project Constitution

版本： v0.1
目標賽事： ASUS UGen AI League — Stage I
專案類型： Offline Video Privacy Processing
核心概念： Context-Aware Sensitive Information Replacement

⸻

1. 我們要做什麼？

PrivacyLens 是一套針對**錄製完成的影片（recorded video）**進行隱私檢查與內容替換的 AI 系統。

系統分析影片中的：

* 畫面內容
* OCR 文字
* 當前場景
* 前後文 context

並判斷：

哪些資訊在目前的 context 下不應該出現在最終公開影片中？

被判定為 sensitive 的內容不只是被 blur 或塗黑，而是盡可能替換成具有語意的 placeholder。

例如：

原始內容：
OPENAI_API_KEY=sk-prod-a83fj29...
ssh admin@203.0.113.xx
Contact: alice@example.com

處理後：

OPENAI_API_KEY=<API_KEY>
ssh admin@<IP_ADDRESS>
Contact: <EMAIL>

我們希望達成：

隱藏資訊的 value，但保留資訊的 meaning。

⸻

2. 我們解決的問題

Creator、工程師、教師或其他使用者在錄製：

* Programming tutorial
* Software demonstration
* Terminal operation
* Development workflow
* Technical presentation
* Screen recording

時，可能無意間錄進不應公開的資訊。

例如：

API Key
Password
Email
IP Address
Internal Hostname
Private Repository
Customer Name
Project Name
Private Notification
.env Content
Terminal History

這些資訊有時可能只出現數秒，因此人工檢查長影片容易遺漏。

PrivacyLens 的目的不是取代使用者所有人工審查，而是在影片發布前提供：

AI-assisted privacy post-processing

⸻

3. 為什麼不能只用 Regex？

如果問題只是：

找到 email → 隱藏
找到 IPv4 → 隱藏
找到 API key → 隱藏

那麼：

OCR
 ↓
Regex
 ↓
Replacement

就已經可以完成。

這不是 PrivacyLens 最主要想解決的問題。

真正困難的是：

一段資訊是否 sensitive，可能取決於它出現的 context，而不是字串本身。

⸻

4. Context-Aware Privacy

例如影片中出現：

Documentation:
API_KEY=<YOUR_API_KEY>

這本來就是教學用 placeholder，因此：

<YOUR_API_KEY>
→ SAFE
→ 不處理

但如果 Terminal 出現：

export API_KEY=sk-prod-A8F31K...

則：

sk-prod-A8F31K...
→ SENSITIVE
→ <API_KEY>

另一個例子：

127.0.0.1

在 localhost tutorial 中可能不需要處理。

但是：

Production Server:
203.0.113.xxx

可能需要被替換。

因此 PrivacyLens 的核心問題是：

[
\boxed{
\text{Content + Context}
\rightarrow
\text{Sensitivity Decision}
}
]

而不是：

[
\text{String Pattern}
\rightarrow
\text{Redaction}
]

⸻

5. AI 在這個 Project 中的角色

AI 的主要角色不是負責把文字塗黑。

AI 負責：

理解影片內容，並判斷資訊在目前 context 下是否具有敏感性。

整體 pipeline：

Recorded Video
      ↓
Frame / Scene Processing
      ↓
OCR + Visual Understanding
      ↓
Context Extraction
      ↓
Context-Aware Sensitive
Information Detection
      ↓
Sensitive Entity Classification
      ↓
Temporal Localization / Tracking
      ↓
Semantic Replacement
      ↓
Privacy-Protected Video

其中最核心的 AI component 是：

Visual / Textual Context
          ↓
     AI Reasoning
          ↓
Sensitive?
   YES / NO
          ↓
Sensitive Type

例如：

"Project Apollo"
+
Internal development meeting context
→ PROJECT_NAME
→ SENSITIVE

但：

"Project Apollo"
+
Public documentation example
→ NOT SENSITIVE

⸻

6. 為什麼使用 Offline Video？

PrivacyLens v1 不是 real-time screen-sharing system。

這是一個刻意的 design decision。

Real-time privacy filtering 需要滿足：

Capture
 +
OCR
 +
AI Reasoning
 +
Replacement
 <
Real-time latency requirement

而且只要原始 frame 在 AI 判斷完成之前被送出，就可能已經造成資訊洩漏。

Offline video processing 沒有這項限制。

我們可以：

Raw Video
    ↓
完整分析
    ↓
Privacy Processing
    ↓
人工確認（optional）
    ↓
Export
    ↓
Publish

因此目前的產品定位是：

在影片發布前，自動檢查並處理可能洩漏的敏感資訊。

Real-time processing 是未來可能的 optimization，而不是目前系統成立的必要條件。

⸻

7. 為什麼是 Replacement，而不是 Blur？

傳統 redaction：

ssh admin@203.0.113.xx
↓
ssh admin@████████████

PrivacyLens：

ssh admin@203.0.113.xx
↓
ssh admin@<IP_ADDRESS>

Blur 可以保護資訊，但同時破壞部分語意。

Semantic replacement 希望同時做到：

Privacy

觀眾無法取得原始 sensitive value。

Context Preservation

觀眾仍然知道：

「這裡原本是一個 IP address。」

因此我們的核心設計原則是：

Hide the value, preserve the meaning.

⸻

8. Hybrid Detection

PrivacyLens 不要求所有東西都交給 AI。

容易 deterministic 判斷的資訊應使用便宜、可靠的方法。

因此系統採：

                    OCR
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   Rule-based Detection    AI Context Analysis
          │                     │
     obvious patterns       ambiguous content
          │                     │
          └──────────┬──────────┘
                     ▼
              Privacy Decision

Rule-based Layer

適合：

Email
IPv4
API-key pattern
Password field
Token pattern

AI Layer

適合：

Internal hostname
Customer name
Project name
Private repository
Internal document
Context-dependent identifier
Ambiguous text

設計原則：

可以 deterministic 解決的問題，不為了「看起來像 AI」而強迫使用 AI。

AI 應該只負責真正需要 semantic/context understanding 的部分。

⸻

9. MVP Scope

Stage I 的 MVP 不需要完成完整 vision。

最低可接受 pipeline：

Short Recorded Video
        ↓
Frame Extraction
        ↓
OCR
        ↓
Sensitive Information Detection
        ↓
Semantic Replacement
        ↓
Output Video

目標測試影片長度：

約 20–60 秒。

至少展示數種資訊：

API Key
Email
IP Address
Password / Token

並至少準備一個案例展示：

相似形式的資訊因 context 不同，而得到不同 privacy decision。

例如：

API_KEY=<YOUR_API_KEY>
→ KEEP
API_KEY=sk-prod-xxxx
→ REPLACE WITH <API_KEY>

這個案例是證明 AI/context-aware component 存在價值的重要 demo。

⸻

10. Replacement Policy

第一版採用 typed semantic placeholder。

例如：

Sensitive Information	Replacement
API key	<API_KEY>
Password	<PASSWORD>
Email	<EMAIL>
IP address	<IP_ADDRESS>
Person	<PERSON>
Customer	<CUSTOMER>
Project name	<PROJECT_NAME>
Internal host	<INTERNAL_HOST>

第一版不要求生成假的 realistic value。

例如：

alice@example.com

優先替換成：

<EMAIL>

而不是生成：

john@example.org

因為 semantic placeholder：

* implementation 更簡單；
* 不會產生 misleading synthetic information；
* privacy meaning 更明確；
* demo 更容易理解。

⸻

11. Stage I Prototype 不需要做到的事情

以下全部屬於 Non-Goals：

* Real-time processing
* Zoom integration
* Google Meet integration
* Teams integration
* Virtual camera
* 30/60 FPS
* 完美重建原本 font
* 完美重建 UI
* Generative inpainting
* 自己訓練大型模型
* Fine-tuning
* 支援所有 PII
* 支援所有 API key format
* Production-grade security
* 保證 zero leakage
* 完全自動取代人工 review
* 手機 App
* Browser extension

除非 MVP、proposal、GitHub、demo 全部已經完成，否則不得因為這些功能延誤投稿。

⸻

12. Stage I Hardware Strategy

Stage I 允許先使用一般 laptop 進行 prototype。

因此：

Stage I
Laptop
 ↓
Video Processing
 ↓
OCR
 ↓
Privacy Analysis
 ↓
Replacement

不要求現在就完成 UGen300 deployment。

Stage II 才規劃：

Video
  ↓
Host
  ↓
UGen300 / Hailo-10H
  ↓
Supported AI Inference
  ↓
Host Privacy Pipeline
  ↓
Protected Video

實際哪些 workload 放到 Hailo-10H，必須根據可部署模型與 runtime 驗證後決定。

不得在 proposal 中宣稱尚未驗證的 hardware performance。

⸻

13. Local AI 原則

PrivacyLens 處理的資料本身可能包含：

* Credentials
* Private documents
* Internal information
* Customer information
* Personal information

因此產品長期方向應優先採取：

On-device / local inference

而不是：

Sensitive Video
      ↓
Upload everything to cloud
      ↓
Ask cloud model what is sensitive

我們的基本論述是：

The information being analyzed for privacy protection should not itself need to be exposed to an external service.

因此 Edge AI 與 PrivacyLens 的問題具有自然關聯，而不是單純為了參賽硬加入 accelerator。

⸻

14. Demo 原則

所有 demo 中的 sensitive information 必須為人造資料。

例如：

sk-demo-123456789
alice@example.com
192.168.10.24
demo-password-123

不得故意使用：

* 真實 API key
* 真實 password
* 真實私人訊息
* 他人的 private information
* 未經允許取得的畫面

Demo 最理想呈現方式：

┌────────────┐
│ RAW VIDEO  │
└──────┬─────┘
       ↓
   PrivacyLens
       ↓
┌────────────┐
│ SAFE VIDEO │
└────────────┘
Before / After

讓觀眾在數秒內理解 project。

⸻

15. 我們不宣稱什麼

PrivacyLens 不宣稱：

「我們發明了 privacy redaction。」

不宣稱：

「我們是第一個使用 AI 保護影片 privacy 的系統。」

不宣稱：

「以前沒有人做過 content replacement。」

不宣稱：

「PrivacyLens 可以保證所有 sensitive information 都不會洩漏。」

我們接受 privacy redaction、PII detection、content replacement 等領域存在 prior work。

我們自己的 project focus 是：

利用 contextual understanding 判斷 recorded video 中哪些資訊需要被保護，並透過 semantic replacement 在隱藏 sensitive value 的同時保留內容語意。

⸻

16. 原創與第三方資源原則

本專案必須由團隊自行完成核心設計、整合、程式與 demo。

可以合法使用：

* Open-source libraries
* Open-source models
* Public documentation
* Published research methods
* 合法取得的 pretrained models

但必須：

* 遵守 license；
* 正確 attribution；
* 在 References 中標示重要來源；
* 不將第三方成果宣稱為自己的發明。

「存在類似 prior work」本身不是我們停止專案的理由。

我們關心的是：

這是不是我們自己完成並依規則合法投稿的作品？

而不是：

世界上是否從來沒有人想到類似問題。

若主辦單位對資格另有正式解釋，以主辦單位規定為準。

⸻

17. Definition of Done — Prototype

Prototype 完成的最低標準：

Input Video
    ↓
成功讀取
    ↓
找到文字
    ↓
辨識 sensitive information
    ↓
決定 KEEP / REPLACE
    ↓
替換 sensitive value
    ↓
輸出 processed video

至少能展示：

Case A — Obvious Sensitive Information

sk-demo-xxxx
→
<API_KEY>

Case B — Context Matters

<YOUR_API_KEY>
→
KEEP

versus

sk-prod-xxxx
→
<API_KEY>

Case C — Context Preservation

Replacement 後，觀眾仍然能理解畫面原本資訊的功能。

⸻

18. Definition of Done — Competition

Prototype 做完 不等於 project 做完。

Stage I 完成必須包含：

* Working prototype
* GitHub repository
* README
* System architecture
* English proposal deck
* Demo video
* YouTube unlisted link
* GitHub link
* References
* ASUS competition submission
* Course submission

我們的首要成功條件是：

在 deadline 前完成一份合規、完整、可以實際展示的 Stage I submission。

⸻

19. Feature Priority

所有功能按照以下順序排序：

1. End-to-End Pipeline Works
              ↓
2. Context-Aware Decision Works
              ↓
3. Replacement Works
              ↓
4. Demo Is Understandable
              ↓
5. Competition Materials Complete
              ↓
6. Improve Detection Accuracy
              ↓
7. Improve Visual Quality
              ↓
8. Optimize Performance
              ↓
9. Real-Time Processing

如果低順位功能會威脅高順位項目的完成時間：

砍掉低順位功能。

⸻

20. Scope Decision Rule

任何新 feature 在加入前，都必須回答：

Question 1

它是否直接幫助證明：

Context-aware privacy detection？

Question 2

它是否直接幫助證明：

Semantic replacement？

Question 3

它是否為 Stage I submission 所必要？

如果三題全部都是：

No

則預設：

Stage I 不做。

⸻

21. Project North Star

當我們不知道某個功能該不該做、某個模型該不該加入、project 是否偏離方向時，回到下面這句話：

PrivacyLens 使用 AI 理解錄製影片中的視覺與文字 context，自動判斷哪些資訊不應被公開，並將 sensitive value 替換成具有語意的 placeholder，使影片在保護隱私的同時仍保留原本的資訊結構與可理解性。

更短的版本：

Hide the value. Preserve the context.

這是 PrivacyLens 的核心。任何功能都應該服務於這個目標。