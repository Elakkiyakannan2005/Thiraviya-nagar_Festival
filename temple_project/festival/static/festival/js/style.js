// =========================
// PAGE LOADED
// =========================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Temple Festival Website Loaded!");


    // =========================
    // CSRF HELPER (Django)
    // =========================

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    const csrftoken = getCookie("csrftoken");


    // =========================
    // MOBILE NAVBAR
    // =========================

    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector("#navLinks");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", function () {
            navLinks.classList.toggle("active");
        });
    }

    document.querySelectorAll("#navLinks a").forEach(function (link) {
        link.addEventListener("click", function () {
            navLinks.classList.remove("active");
        });
    });


    // =========================
    // BACKGROUND VIDEO
    // =========================

    const backgroundVideo = document.querySelector(".background-video");

    if (backgroundVideo) {
        backgroundVideo.play().catch(function () {
            console.log("Video autoplay blocked.");
        });
    }


    // =========================
    // DONATION AMOUNT BUTTONS
    // =========================

    const amountButtons = document.querySelectorAll(".amounts button");
    const amountInput = document.querySelector("#amount");

    amountButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            amountInput.value = button.getAttribute("data-amount");

            amountButtons.forEach(function (btn) {
                btn.classList.remove("active");
            });

            button.classList.add("active");
        });
    });


    // =========================
    // DONATION FORM -> DJANGO BACKEND
    // =========================

    const donationForm = document.querySelector("#donationForm");
    const formMessage = document.querySelector("#formMessage");

    if (donationForm) {

        donationForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const formData = new FormData(donationForm);
            const payload = {
                name: formData.get("name"),
                mobile: formData.get("mobile"),
                address: formData.get("address"),
                amount: formData.get("amount"),
            };

            if (!payload.amount || Number(payload.amount) <= 0) {
                showFormMessage("Please enter a valid donation amount.", false);
                return;
            }

            fetch(donationForm.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify(payload),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, data: data };
                    });
                })
                .then(function (result) {
                    showFormMessage(result.data.message, result.ok);

                    if (result.ok) {
                        donationForm.reset();

                        amountButtons.forEach(function (btn) {
                            btn.classList.remove("active");
                        });

                        if (result.data.receipt_url) {
                            showReceiptLink(result.data.receipt_url, result.data.receipt_number);
                        }

                        if (typeof result.data.total_raised === "number") {
                            animateCounter(
                                document.querySelector('.stat-number[data-count-to]'),
                                result.data.total_raised
                            );
                        }
                        if (typeof result.data.donor_count === "number") {
                            const donorStat = document.querySelectorAll(".stat-number[data-count-to]")[1];
                            animateCounter(donorStat, result.data.donor_count);
                        }
                    }
                })
                .catch(function () {
                    showFormMessage("Something went wrong. Please try again.", false);
                });
        });
    }

    function showFormMessage(text, ok) {
        formMessage.textContent = text;
        formMessage.style.color = ok ? "#526d39" : "#a33b3b";
        formMessage.classList.remove("success-flash");
        // restart animation
        void formMessage.offsetWidth;
        formMessage.classList.add("success-flash");
    }

    function showReceiptLink(url, receiptNumber) {
        let link = document.querySelector("#receiptLink");

        if (!link) {
            link = document.createElement("a");
            link.id = "receiptLink";
            link.className = "btn primary receipt-link";
            link.target = "_blank";
            link.rel = "noopener";
            formMessage.insertAdjacentElement("afterend", link);
        }

        link.href = url;
        link.textContent = receiptNumber
            ? `Download Receipt (${receiptNumber}) →`
            : "Download Receipt →";
        link.style.display = "inline-block";
    }


    // =========================
    // ANIMATED COUNTERS (donation stats)
    // =========================

    function animateCounter(el, target) {
        if (!el) return;

        const duration = 1200;
        const start = performance.now();
        const from = 0;

        function step(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.floor(from + (target - from) * eased);
            el.textContent = value.toLocaleString("en-IN");

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = Math.round(target).toLocaleString("en-IN");
            }
        }

        requestAnimationFrame(step);
    }

    const counterEls = document.querySelectorAll(".stat-number[data-count-to]");

    const counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                const target = Number(entry.target.getAttribute("data-count-to")) || 0;
                animateCounter(entry.target, target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.4 });

    counterEls.forEach(function (el) {
        counterObserver.observe(el);
    });


    // =========================
    // SCROLL REVEAL (sections + cards + gallery + form)
    // =========================

    const revealTargets = document.querySelectorAll(".section, .animate-on-scroll");

    const revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("in-view");

                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";

                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    revealTargets.forEach(function (section) {
        if (!section.classList.contains("animate-on-scroll")) {
            section.style.opacity = "0";
            section.style.transform = "translateY(20px)";
            section.style.transition = "opacity 0.6s ease, transform 0.6s ease";
        }

        revealObserver.observe(section);
    });


    console.log("All JavaScript features loaded!");

});
