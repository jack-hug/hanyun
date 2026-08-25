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


// 鼠标划过时时出现效果
$(document).ready(function () {
    $('.company-hover').on('mouseenter', function () {
        $(this).closest('.row').find('.company-image-style').addClass('hovered');
    });

    $('.company-hover').on('mouseleave', function () {
        $(this).closest('.row').find('.company-image-style').removeClass('hovered');
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

// slick 图片滚动
$(document).ready(function () {
    $('.slick-item').slick({
        infinite: true,
        speed: 1000,
        slidesToShow: 5,
        adaptiveHeight: true,
        autoplay: true,
        autoplaySpeed: 1000,
        pauseOnHover: true,
        arrows: false,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 5,
                    slidesToScroll: 1,
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 1
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1
                }
            }
        ]

    });
});


//  产品缩略图放大效果

// 图片放大镜功能
document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.magnifier-container');
    const mainImage = document.getElementById('main-image');
    const lens = document.getElementById('lens');
    const result = document.getElementById('result');
    const resultImage = document.getElementById('result-image');

    if (!container || !mainImage || !lens || !result || !resultImage) return;

    let isHovering = false;

    // 设置放大倍数
    const magnify = 1.5;

    // 获取容器和图片的尺寸
    function getDimensions() {
        const containerRect = container.getBoundingClientRect();
        const imageRect = mainImage.getBoundingClientRect();

        // 获取图片实际显示尺寸
        const displayWidth = imageRect.width;
        const displayHeight = imageRect.height;

        // 获取图片原始尺寸（通过自然尺寸）
        const naturalWidth = mainImage.naturalWidth || displayWidth;
        const naturalHeight = mainImage.naturalHeight || displayHeight;

        return {
            containerRect,
            imageRect,
            displayWidth,
            displayHeight,
            naturalWidth,
            naturalHeight
        };
    }

    // 更新结果窗口位置（避免超出视口）
    function updateResultPosition(mouseX, mouseY) {
        const resultWidth = 500;
        const resultHeight = 500;

        // 默认显示在右侧
        let left = mouseX + 20;
        let top = mouseY - resultHeight / 2;

        // 如果右侧空间不足，显示在左侧
        if (left + resultWidth > window.innerWidth) {
            left = mouseX - resultWidth - 20;
        }

        // 如果左侧空间也不足，贴近右侧边缘
        if (left < 0) {
            left = 10;
        }

        // 垂直方向调整
        if (top < 10) {
            top = 10;
        }
        if (top + resultHeight > window.innerHeight - 10) {
            top = window.innerHeight - resultHeight - 10;
        }

        result.style.left = left + 'px';
        result.style.top = top + 'px';
    }

    // 更新放大效果
    function updateMagnification(e) {
        if (!isHovering) return;

        const dims = getDimensions();
        const rect = dims.imageRect;

        // 计算鼠标在图片上的位置（百分比）
        let x = (e.clientX - rect.left) / rect.width;
        let y = (e.clientY - rect.top) / rect.height;

        // 限制范围
        x = Math.max(0, Math.min(1, x));
        y = Math.max(0, Math.min(1, y));

        // 更新镜头位置
        const lensSize = 150;
        const lensX = (e.clientX - rect.left - lensSize / 2);
        const lensY = (e.clientY - rect.top - lensSize / 2);

        lens.style.left = Math.max(0, Math.min(rect.width - lensSize, lensX)) + 'px';
        lens.style.top = Math.max(0, Math.min(rect.height - lensSize, lensY)) + 'px';

        // 更新放大图片
        // 计算图片的自然尺寸与显示尺寸的比例
        const scaleX = dims.naturalWidth / rect.width;
        const scaleY = dims.naturalHeight / rect.height;

        // 计算在自然图片中的位置
        const naturalX = x * dims.naturalWidth;
        const naturalY = y * dims.naturalHeight;

        // 计算结果窗口中图片的显示大小
        const resultWidth = 500;
        const resultHeight = 500;

        // 根据放大倍数计算显示区域
        const displayWidth = resultWidth / magnify;
        const displayHeight = resultHeight / magnify;

        // 计算在自然图片中需要显示的区域
        const viewX = naturalX - displayWidth / 2;
        const viewY = naturalY - displayHeight / 2;

        // 设置背景图片位置
        resultImage.style.left = -viewX * (resultWidth / displayWidth) + 'px';
        resultImage.style.top = -viewY * (resultHeight / displayHeight) + 'px';
        resultImage.style.width = (dims.naturalWidth * (resultWidth / displayWidth)) + 'px';
        resultImage.style.height = (dims.naturalHeight * (resultHeight / displayHeight)) + 'px';

        // 更新结果窗口位置
        updateResultPosition(e.clientX, e.clientY);
    }

    // 鼠标进入容器
    container.addEventListener('mouseenter', function (e) {
        isHovering = true;
        lens.style.display = 'block';
        result.style.display = 'block';

        // 初始化镜头大小
        const rect = mainImage.getBoundingClientRect();
        lens.style.width = '150px';
        lens.style.height = '150px';

        // 初始化结果图片
        const imgSrc = mainImage.src;
        resultImage.src = imgSrc;

        // 更新放大效果
        updateMagnification(e);
    });

    // 鼠标在容器中移动
    container.addEventListener('mousemove', function (e) {
        if (isHovering) {
            updateMagnification(e);
        }
    });

    // 鼠标离开容器
    container.addEventListener('mouseleave', function () {
        isHovering = false;
        lens.style.display = 'none';
        result.style.display = 'none';
    });

    // 窗口大小变化时重新计算
    window.addEventListener('resize', function () {
        if (isHovering) {
            const rect = mainImage.getBoundingClientRect();
            lens.style.width = '150px';
            lens.style.height = '150px';
        }
    });
});

// 缩略图切换功能
function switchImage(element) {
    // 更新主图
    const mainImage = document.getElementById('main-image');
    const resultImage = document.getElementById('result-image');
    const newSrc = element.getAttribute('data-target');

    if (mainImage && newSrc) {
        mainImage.src = newSrc;
        // 同时更新放大结果图
        if (resultImage) {
            resultImage.src = newSrc;
        }
    }

    // 更新缩略图激活状态
    document.querySelectorAll('.thumbnail-image').forEach(thumb => {
        thumb.classList.remove('active');
    });
    element.classList.add('active');
}