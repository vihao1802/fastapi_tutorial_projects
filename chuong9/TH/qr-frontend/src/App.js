import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [url, setUrl] = useState('');
  const [qrImage, setQrImage] = useState(null);
  const [error, setError] = useState('');

  const handleGenerate = async (e) => {
    e.preventDefault();
  
    const formData = new FormData();
    formData.append("url", url);
  
    try {
      const response = await axios.post("http://localhost:8000/generate", formData, {
        responseType: "blob"
      });
  
      const imageUrl = URL.createObjectURL(response.data);
      setQrImage(imageUrl);
      setError('');
    } catch (err) {
      setQrImage(null);
  
      if (err.response?.data instanceof Blob) {
        const text = await err.response.data.text();
        setError(text);
      } else {
        setError(err.response?.data || 'Link không hợp lệ hoặc lỗi spam quá nhiều');
      }
    }
  };
  
  

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h2>QR Code Generator</h2>
      <form onSubmit={handleGenerate}>
        <input type="text" value={url} onChange={e => setUrl(e.target.value)} placeholder="Nhập URL..." />
        <button type="submit">Tạo mã QR</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {qrImage && <img src={qrImage} alt="QR Code" />}
    </div>
  );
}

export default App;
