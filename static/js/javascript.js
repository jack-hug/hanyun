// 鼠标移入翻转元素
let isFlipped = false;

document.addEventListener('DOMContentLoaded', function () {
    let flipElements = document.getElementsByClassName('flipElement');

    Array.from(flipElements).forEach(function (flipElement) {
        let isFlipped = false;

        flipElement.addEventListener('mouseenter', function () {
            let icon = this.querySelector('.circle-body');
            if (icon) {
                if (!isFlipped) {
                    icon.style.transform = 'rotateY(360deg)';
                    isFlipped = true;
                } else {
                    icon.style.transform = 'rotateY(0deg)';
                    isFlipped = false;
                }
            }
        });

        flipElement.addEventListener('mouseleave', function () {
            // 不需要重置 isFlipped，因为 mouseenter 事件会处理翻转状态
        });
    });
});

// 产品页缩略图切换
document.addEventListener('DOMContentLoaded', function () {
    const mainImage = document.getElementById('main-image');
    const thumbnails = document.querySelectorAll('.thumbnail-image');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('mouseover', function () {
            const targetImage = this.getAttribute('data-target');
            mainImage.src = targetImage;
            // 移除所有小图的 active 类
            thumbnails.forEach(thumb => thumb.classList.remove('active'));
            // 为当前小图添加 active 类
            this.classList.add('active');
        });

        thumbnail.addEventListener('mouseout', function () {
            // 移除当前小图的 active 类
            this.classList.remove('active');
        });
    });
});


// 鼠标划过.advantage-style时出现advantage-image-hover效果
$(document).ready(function () {
    $('.advantage-style').on('mouseenter', function () {
        $(this).siblings('.advantage-image-hover').addClass('hovered');
    });

    $('.advantage-style').on('mouseleave', function () {
        $(this).siblings('.advantage-image-hover').removeClass('hovered');
    });
});

// 秒后自动关闭flash消息
document.addEventListener("DOMContentLoaded", function () {
    // 获取所有带有 flash-message 类的 alert 元素
    var alerts = document.querySelectorAll('.alert-floating');
    alerts.forEach(function (alert) {
        // 5 秒后自动关闭 alert
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
