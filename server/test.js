import dotenv from "dotenv";
import axios from "axios";

dotenv.config();

const keyArray = JSON.parse(process.env.GEMINI_API_KEYS);

async function testAllAPIKeys() {
  for (const key of keyArray) {
    const res = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${key}`,
      {
        contents: [
          {
            parts: [{ text: "Give me python code to sort a list." }],
          },
        ],
      }
    );
    console.log(res.data.candidates[0].content.parts[0].text);
  }
}

testAllAPIKeys();
