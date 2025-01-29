import base64
import gradio as gr
from mlc_llm import MLCEngine


with open("./assets/long_logo.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')


header_html = """
<style>
.header-main {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 20px;
}

.header-content {
    flex: 1;
}

h1 {
    text-align: left;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    font-size: 1.8rem;
}

.model-description {
    text-align: left;
    color: #64748b;
    margin: 0.5rem 0;
    padding: 4px 0;
    line-height: 2.0;
}

.model-description a {
    color: #2563eb;
    text-decoration: none;
}

.model-description a:hover {
    text-decoration: underline;
}

.logo {
    height: 35px;
    background-color: white;
    padding: 5px;
    border-radius: 5px;
}
</style>

<div class="header-main">
    <div class="header-content">
        <h1>TinySwallow ChatUI Local</h1>
        <p class="model-description">
            📚 <a href="https://arxiv.org/abs/2501.16937" target="_blank">Paper</a> | 
            🤗 <a href="https://huggingface.co/collections/SakanaAI/tinyswallow-676cf5e57fff9075b5ddb7ec" target="_blank">Hugging Face</a> | 
            📝 <a href="https://sakana.ai/taid-jp" target="_blank">Blog</a><br>
            完全オフラインで動作するTinySwallow-1.5Bのチャットデモです。モデルの重みをローカルから直接読み込んでチャットができます。
        </p>
    </div>
"""
header_html += f"""    <img src="data:image/png;base64,{encoded_image}" alt="Sakana AI Logo" class="logo" width="100" height="100"/>
</div>
"""
class ChatBot:
    def __init__(self):
        self.engine = None
        self.system_prompt = [
            {
                "role": "system",
                "content": "あなたは、Sakana AI株式会社が開発したTinySwallowです。小型ながら、誠実で優秀なアシスタントです。"
            }
        ]
        self.model = "./model"
    
    def initialize_engine(self):
        if self.engine is None:
            self.engine = MLCEngine(self.model)
    
    def generate_response(self, message, history):
        # Initialize engine if not already done
        self.initialize_engine()
        
        # Add user message to messages
        history = self.system_prompt + history
        history.append({"role": "user", "content": message})
        
        # Generate response
        response_text = ""
        for response in self.engine.chat.completions.create(
            messages=history,
            model=self.model,
            stream=True,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.5,
        ):
            for choice in response.choices:
                delta_content = choice.delta.content
                if delta_content:
                    response_text += delta_content
                    yield response_text
                
def create_ui():
    chatbot = ChatBot()
    
    
    
    with gr.Blocks() as demo:
        gr.HTML(header_html)
        # gr.Markdown("""📚 [Paper](https://arxiv.org/abs/2501.16937) | 
        # 🤗 [Hugging Face](https://huggingface.co/collections/SakanaAI/tinyswallow-676cf5e57fff9075b5ddb7ec) | 
        # 📝 [Blog](https://sakana.ai/taid-jp)
        
        # 完全オフラインで動作するTinySwallow-1.5Bのチャットデモです。モデルの重みをローカルから直接読み込んでチャットができます。
        # """)
        
        chatbot_interface = gr.ChatInterface(
            chatbot.generate_response,
            examples=[
                "年始挨拶のメールテンプレートを作ってください。",
                "知識蒸留について簡単に教えてください。",
                "これから大事な発表があります。私を励ましてください。",
                "２羽のツバメが主人公の温かな物語を書いてください。"
            ],
            example_icons=["✉️", "🧠", "💪", "🐦"],
            chatbot=gr.Chatbot(type="messages"),
            textbox=gr.Textbox(placeholder="メッセージを入力してください。", scale=7),
            title="",
            type="messages",
        )

        with gr.Accordion("利用上の注意事項", open=False):
            gr.Markdown("""
            本モデルは実験段階のプロトタイプであり、研究開発の目的でのみ提供されています。商用利用や、障害が重大な影響を及ぼす可能性のある環境（ミッションクリティカルな環境）での使用には適していません。 本モデルの使用は、利用者の自己責任で行われ、その性能や結果については何ら保証されません。 Sakana AIは、本モデルの使用によって生じた直接的または間接的な損失に対して、結果に関わらず、一切の責任を負いません。 利用者は、本モデルの使用に伴うリスクを十分に理解し、自身の判断で使用することが必要です。
            
            本モデルはGoogleの「Gemma」モデルの派生物です。ご利用にあたっては、[Gemma Terms of Use](https://ai.google.dev/gemma/terms)および[Gemma Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy)を遵守してください。モデルの出力は現状有姿で提供され、正確性や適法性などは保証されません。禁止行為が確認された場合、予告なく利用を制限または停止することがあります。
            """)

    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        # server_name="0.0.0.0",
        # server_port=8000,
        inbrowser=True,
        share=False,
        favicon_path="./assets/logo.png",
        debug=True,
    )
