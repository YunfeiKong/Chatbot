import axios from 'axios';

const LLM_API_ENDPOINT = `${process.env.REACT_APP_API_BASE_URL}/`;

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(LLM_API_ENDPOINT + 'upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('文件上传失败:', error);
    throw error;
  }
};

export const ChatToLLM = async (text) => {
  try {
    const response = await axios.post(LLM_API_ENDPOINT + 'llm_chat', { text });
    return response.data;
  } catch (error) {
    console.error('LLM Chat API 请求失败:', error);
    throw error;
  }
}
