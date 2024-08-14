// 鼠标移入翻转元素
let isFlipped = false;

document.addEventListener('DOMContentLoaded', function() {
    let flipElements = document.getElementsByClassName('flipElement');

    Array.from(flipElements).forEach(function(flipElement) {
        let isFlipped = false;

        flipElement.addEventListener('mouseenter', function() {
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

        flipElement.addEventListener('mouseleave', function() {
            // 不需要重置 isFlipped，因为 mouseenter 事件会处理翻转状态
        });
    });
});