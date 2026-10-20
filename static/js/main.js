/**
 * SoleStride E-Commerce & Concurrency JS Engine
 * High-performance, modular, reactive micro-interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    initToasts();
    initQuickView();
    initAddToCart();
    initCartDrawer();
    initLiveChat();
    initTrackingHelpers();
});

// Helper: Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 1. Toast Notification System
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const bgClass = type === 'success' ? 'bg-success' : (type === 'danger' ? 'bg-danger' : 'bg-primary');
    const icon = type === 'success' ? 'bi-check-circle-fill' : 'bi-info-circle-fill';

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white ${bgClass} border-0 shadow-lg mb-2`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="bi ${icon} fs-5"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function initToasts() {
    if (!document.getElementById('toastContainer')) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
}

// 2. Add To Cart System (AJAX)
function initAddToCart() {
    document.querySelectorAll('.btn-add-to-cart-ajax').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const shoeId = button.getAttribute('data-shoe-id');
            const shoeTitle = button.getAttribute('data-shoe-title') || 'Shoe';
            const sizeSelector = document.querySelector(`input[name="shoe_size_${shoeId}"]:checked`) || 
                                 document.querySelector('.shoe-size-active') ||
                                 document.getElementById('quickViewSizeSelect');
            
            const size = sizeSelector ? (sizeSelector.value || sizeSelector.getAttribute('data-size')) : '9.5';
            const originalContent = button.innerHTML;
            button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> Adding...`;
            button.disabled = true;

            try {
                const response = await fetch('/api/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        shoe_id: shoeId,
                        size: size,
                        quantity: 1
                    })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    updateCartBadge(data.cart_count);
                    refreshCartOffcanvas();
                } else {
                    showToast(data.message || 'Error adding shoe to bag', 'danger');
                }
            } catch (err) {
                console.error('Add to cart error:', err);
                showToast('Failed to connect to cart service.', 'danger');
            } finally {
                button.innerHTML = originalContent;
                button.disabled = false;
            }
        });
    });
}

function updateCartBadge(count) {
    document.querySelectorAll('.cart-badge-count').forEach(el => {
        el.textContent = count;
        el.style.display = count > 0 ? 'inline-block' : 'none';
    });
}

// 3. Quick View Modal Dynamic Population
function initQuickView() {
    const quickModal = document.getElementById('quickViewModal');
    if (!quickModal) return;

    quickModal.addEventListener('show.bs.modal', (e) => {
        const trigger = e.relatedTarget;
        if (!trigger) return;

        const title = trigger.getAttribute('data-shoe-title');
        const brand = trigger.getAttribute('data-shoe-brand');
        const price = trigger.getAttribute('data-shoe-price');
        const origPrice = trigger.getAttribute('data-shoe-orig-price');
        const image = trigger.getAttribute('data-shoe-image');
        const desc = trigger.getAttribute('data-shoe-desc');
        const id = trigger.getAttribute('data-shoe-id');
        const slug = trigger.getAttribute('data-shoe-slug');

        document.getElementById('qvShoeTitle').textContent = title;
        document.getElementById('qvShoeBrand').textContent = brand;
        document.getElementById('qvShoePrice').textContent = `$${price}`;
        document.getElementById('qvShoeImage').src = image;
        document.getElementById('qvShoeDesc').textContent = desc;
        
        const origEl = document.getElementById('qvShoeOrigPrice');
        if (origPrice && parseFloat(origPrice) > parseFloat(price)) {
            origEl.textContent = `$${origPrice}`;
            origEl.style.display = 'inline';
        } else {
            origEl.style.display = 'none';
        }

        const viewDetailBtn = document.getElementById('qvDetailBtn');
        if (viewDetailBtn && slug) {
            viewDetailBtn.href = `/shoe/${slug}/`;
        }

        const qvAddBtn = document.getElementById('qvAddToCartBtn');
        if (qvAddBtn) {
            qvAddBtn.setAttribute('data-shoe-id', id);
            qvAddBtn.setAttribute('data-shoe-title', title);
        }
    });
}

// 4. Interactive Cart Drawer & Update Items
async function refreshCartOffcanvas() {
    const cartItemsContainer = document.getElementById('cartDrawerItems');
    const cartDrawerSubtotal = document.getElementById('cartDrawerSubtotal');
    if (!cartItemsContainer) return;

    try {
        const response = await fetch('/api/cart/status/');
        const data = await response.json();

        updateCartBadge(data.count);
        if (cartDrawerSubtotal) cartDrawerSubtotal.textContent = `$${data.subtotal}`;

        if (!data.items || data.items.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-bag-x text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-3">Your shopping bag is empty.</p>
                    <a href="/store/" class="btn btn-sole-primary btn-sm mt-2">Explore Shoes</a>
                </div>
            `;
            return;
        }

        let html = '';
        data.items.forEach(it => {
            html += `
                <div class="d-flex align-items-center gap-3 py-3 border-bottom border-secondary border-opacity-25" id="cart-item-row-${it.id}">
                    <img src="${it.image}" alt="${it.title}" class="rounded" style="width: 70px; height: 70px; object-fit: cover; background: #0c0f17;">
                    <div class="flex-grow-1">
                        <h6 class="mb-1 text-white fs-6">${it.title}</h6>
                        <div class="d-flex align-items-center gap-2 text-muted small">
                            <span>US ${it.size}</span>
                            <span>&bull;</span>
                            <span class="text-white fw-bold">$${it.price}</span>
                        </div>
                        <div class="d-flex align-items-center gap-2 mt-2">
                            <button class="btn btn-sm btn-outline-secondary py-0 px-2 text-white" onclick="updateCartItemQty(${it.id}, 'decrease')">-</button>
                            <span class="small fw-bold px-1">${it.quantity}</span>
                            <button class="btn btn-sm btn-outline-secondary py-0 px-2 text-white" onclick="updateCartItemQty(${it.id}, 'increase')">+</button>
                            <button class="btn btn-sm text-danger ms-auto p-0" onclick="updateCartItemQty(${it.id}, 'remove')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        cartItemsContainer.innerHTML = html;
    } catch (e) {
        console.error('Failed refreshing cart drawer', e);
    }
}

async function updateCartItemQty(itemId, action) {
    try {
        const response = await fetch('/api/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ item_id: itemId, action: action })
        });
        const data = await response.json();
        if (data.status === 'success') {
            updateCartBadge(data.cart_count);
            refreshCartOffcanvas();
            if (window.location.pathname.includes('/cart/')) {
                window.location.reload();
            }
        }
    } catch (e) {
        showToast('Error updating item quantity', 'danger');
    }
}

function initCartDrawer() {
    const cartOffcanvas = document.getElementById('cartOffcanvas');
    if (cartOffcanvas) {
        cartOffcanvas.addEventListener('show.bs.offcanvas', () => {
            refreshCartOffcanvas();
        });
    }
}

// 5. Live AI / Concierge Chatbot Widget
function initLiveChat() {
    const chatBtn = document.getElementById('chatWidgetBtn');
    const chatModal = document.getElementById('chatBoxModal');
    const chatClose = document.getElementById('chatCloseBtn');
    const chatForm = document.getElementById('chatInputForm');
    const chatInput = document.getElementById('chatInputText');
    const chatBody = document.getElementById('chatBodyMessages');

    if (!chatBtn || !chatModal) return;

    chatBtn.addEventListener('click', () => {
        chatModal.classList.toggle('show');
        if (chatModal.classList.contains('show')) {
            chatInput.focus();
        }
    });

    if (chatClose) {
        chatClose.addEventListener('click', () => chatModal.classList.remove('show'));
    }

    const botKnowledge = [
        {
            keywords: ['track', 'order', 'delivery', 'where', 'shipping', 'status'],
            reply: 'You can track any active shipment in real time on our <a href="/track/" class="text-warning text-decoration-underline">Track Order Page</a> using your code (e.g., <strong>STRIDE-8842-NY</strong>)!'
        },
        {
            keywords: ['size', 'fit', 'sizing', 'small', 'large'],
            reply: 'Our performance runners fit true to size (TTS). If you have wider feet, we recommend ordering half a size up (e.g., US 10.5 instead of US 10.0).'
        },
        {
            keywords: ['return', 'refund', 'warranty', 'exchange'],
            reply: 'We offer a 30-Day Risk-Free Trial! If the fit isn\'t perfect, return them in pristine condition for a 100% full refund with prepaid return labels.'
        },
        {
            keywords: ['authentic', 'real', 'original', 'fake'],
            reply: 'Every pair at SoleStride comes with a verified holographic authenticity NFC tag and multi-point master inspection before dispatch.'
        },
        {
            keywords: ['coupon', 'discount', 'promo', 'code'],
            reply: 'Use promo code <strong>KICKS20</strong> at checkout for 20% off your entire order today!'
        }
    ];

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = chatInput.value.trim();
            if (!text) return;

            const userMsg = document.createElement('div');
            userMsg.className = 'chat-bubble user';
            userMsg.textContent = text;
            chatBody.appendChild(userMsg);
            chatInput.value = '';
            chatBody.scrollTop = chatBody.scrollHeight;

            const typingBubble = document.createElement('div');
            typingBubble.className = 'chat-bubble bot text-muted';
            typingBubble.id = 'botTyping';
            typingBubble.innerHTML = '<span class="spinner-grow spinner-grow-sm me-1" role="status"></span> Specialist typing...';
            chatBody.appendChild(typingBubble);
            chatBody.scrollTop = chatBody.scrollHeight;

            setTimeout(() => {
                typingBubble.remove();
                const lower = text.toLowerCase();
                let matched = botKnowledge.find(item => item.keywords.some(k => lower.includes(k)));
                let responseText = matched 
                    ? matched.reply 
                    : "Thanks for reaching out! Our footwear concierge team is available 24/7. You can also submit an official ticket via our <a href='/helpline/' class='text-warning text-decoration-underline'>Helpline Center</a>.";

                const botMsg = document.createElement('div');
                botMsg.className = 'chat-bubble bot';
                botMsg.innerHTML = responseText;
                chatBody.appendChild(botMsg);
                chatBody.scrollTop = chatBody.scrollHeight;
            }, 600);
        });
    }

    document.querySelectorAll('.chat-quick-prompt').forEach(chip => {
        chip.addEventListener('click', () => {
            if (chatInput) {
                chatInput.value = chip.textContent;
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });
}

// 6. Tracking page helpers (copy button & sample fills)
function initTrackingHelpers() {
    document.querySelectorAll('.btn-fill-tracking').forEach(btn => {
        btn.addEventListener('click', () => {
            const code = btn.getAttribute('data-code');
            const input = document.getElementById('trackingCodeInput');
            if (input && code) {
                input.value = code;
                input.form.submit();
            }
        });
    });

    const copyBtn = document.getElementById('copyTrackingBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const code = copyBtn.getAttribute('data-code');
            navigator.clipboard.writeText(code).then(() => {
                showToast(`Tracking code ${code} copied to clipboard!`, 'success');
            });
        });
    }
}
