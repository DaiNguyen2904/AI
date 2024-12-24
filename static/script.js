document.getElementById("submitBtn").addEventListener("click", function () {
  const userId = document.getElementById("userIdInput").value; // Thay đổi thành lấy ID người dùng

  if (!userId) {
    alert("Vui lòng nhập ID người dùng!");
    return;
  }

  // Gửi request đến Flask
  fetch("/recommend", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ user_id: userId }) // Thay đổi thành gửi ID người dùng
  })
    .then(response => response.json())
    .then(data => {
      const resultTable = document.getElementById("resultTable").querySelector("tbody");
      resultTable.innerHTML = ""; // Xóa kết quả cũ

      if (data.recommendations && data.recommendations.length > 0) {
        data.recommendations.forEach((movie, index) => {
          const row = `<tr class="${index % 2 === 0 ? 'bg-gray-100' : 'bg-white'}">
            <td class="py-2 px-4 border-b border-gray-300">${movie.id}</td>
            <td class="py-2 px-4 border-b border-gray-300">${movie.title}</td>
            <td class="py-2 px-4 border-b border-gray-300">${movie.genres}</td>
          </tr>`;
          resultTable.insertAdjacentHTML("beforeend", row);
        });
      } else {
        resultTable.innerHTML = '<tr><td colspan="3" class="py-2 px-4 text-center">Không tìm thấy gợi ý</td></tr>';
      }
    })
    .catch(error => console.error("Error:", error));
});
