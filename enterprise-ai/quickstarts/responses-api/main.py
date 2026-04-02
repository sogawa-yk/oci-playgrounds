import os

import httpx
from dotenv import load_dotenv
from oci_genai_auth import OciUserPrincipalAuth
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://inference.generativeai.ap-osaka-1.oci.oraclecloud.com/openai/v1",
    api_key="not-used",
    project=os.environ["OCI_GENAI_PROJECT"],
    http_client=httpx.Client(auth=OciUserPrincipalAuth(profile_name="DEFAULT")),
)

response = client.responses.create(
    model="openai.gpt-oss-120b",
    input="Oracle Cloud Infrastructureとはなんですか？100文字程度で教えて下さい。",
)

print(response.output_text)
