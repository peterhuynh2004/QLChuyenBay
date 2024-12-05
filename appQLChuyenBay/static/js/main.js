function kiemTraThongTin(nextStep) {
    //tạo 1 biến giữ trạng thái thông tin hợp lệ
    let isValid = true;

    // Kiểm tra họ và tên
    const fullName = document.getElementById('fullName');
    const fullNameError = document.getElementById('fullNameError');
    if (fullName.value.trim() === '') {
        fullNameError.textContent = 'Họ và tên không được để trống.';
        isValid = false;
    } else {
        fullNameError.textContent = '';
    }

    // Kiểm tra số điện thoại
    const phone = document.getElementById('phone');
    const phoneError = document.getElementById('phoneError');
    const phoneRegex = /^[0-9]{10}$/; //sử dụng biểu thức chính quy để kiểm tra định dạng email
    if (!phoneRegex.test(phone.value)) {
        phoneError.textContent = 'Số điện thoại phải là 10 chữ số.';
        isValid = false;
    } else {
        phoneError.textContent = '';
    }

    // Kiểm tra email
    const email = document.getElementById('email');
    const emailError = document.getElementById('emailError');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
        emailError.textContent = 'Email không hợp lệ.';
        isValid = false;
    } else {
        emailError.textContent = '';
    }

    // Kiểm tra căn cước công dân (CCCD)
    const cccd = document.getElementById('cccd');
    const cccdError = document.getElementById('cccdError');
    const cccdRegex = /^[0-9]{12}$/;
    if (!cccdRegex.test(cccd.value)) {
        cccdError.textContent = 'CCCD phải là 12 chữ số.';
        isValid = false;
    } else {
        cccdError.textContent = '';
    }

    if (isValid) {
        nextForm(nextStep); // Di chuyển đến bước tiếp theo
    }
}

function nextForm(step) {
    const currentForm = document.querySelector('.form-container.active');
    currentForm.classList.remove('active');
    document.getElementById(`formStep${step}`).classList.add('active');
}

function prevForm(step) {
    const currentForm = document.querySelector('.form-container.active');
    currentForm.classList.remove('active');
    document.getElementById(`formStep${step}`).classList.add('active');
}



function kiemtrakhuhoi() {
      const returnCheckbox = document.getElementById("return-checkbox");
      const returnDate = document.getElementById("return-date");

      //Bật hoặc tắt trường ngày về dựa trên trạng thái checkbox
      returnDate.disabled = !returnCheckbox.checked;
    }