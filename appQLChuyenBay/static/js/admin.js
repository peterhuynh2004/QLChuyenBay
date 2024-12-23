// Tạo sự kiện thanh aside
const sideMenu = document.querySelector('aside');
const menuBtn = document.querySelector('#menu_bar');
const closeBtn = document.querySelector('#close_btn');
const themeToggler = document.querySelector('.theme-toggler');

//menuBtn.addEventListener('click', () => {
//    sideMenu.style.display = "block";
//});
//
//closeBtn.addEventListener('click', () => {
//    sideMenu.style.display = "none";
//});

 // Chuyển đổi Light/Dark Mode
    if (themeToggler) {
        themeToggler.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme-variables');

            const span1 = themeToggler.querySelector('span:nth-child(1)');
            const span2 = themeToggler.querySelector('span:nth-child(2)');

            if (span1) span1.classList.toggle('active');
            if (span2) span2.classList.toggle('active');
        });
}