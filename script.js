document.addEventListener("DOMContentLoaded", () => {
    const menuToggle = document.getElementById("menuToggle");
    const siteNav = document.getElementById("siteNav");
    const navLinks = siteNav ? siteNav.querySelectorAll("a") : [];
    const revealItems = document.querySelectorAll(".reveal");
    const complaintForm = document.getElementById("complaintForm");
    const complaintList = document.getElementById("complaintList");
    const formMessage = document.getElementById("formMessage");
    const directorySearch = document.getElementById("directorySearch");
    const filterButtons = document.querySelectorAll(".filter-btn");
    const directoryCards = document.querySelectorAll(".directory-card");

    if (menuToggle && siteNav) {
        menuToggle.addEventListener("click", () => {
            const isOpen = siteNav.classList.toggle("open");
            menuToggle.classList.toggle("open", isOpen);
            menuToggle.setAttribute("aria-expanded", String(isOpen));
        });

        navLinks.forEach((link) => {
            link.addEventListener("click", () => {
                siteNav.classList.remove("open");
                menuToggle.classList.remove("open");
                menuToggle.setAttribute("aria-expanded", "false");
            });
        });
    }

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("reveal-visible");
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.16
    });

    revealItems.forEach((item) => revealObserver.observe(item));

    if (complaintForm && complaintList) {
        complaintForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const name = document.getElementById("residentName").value.trim();
            const phone = document.getElementById("residentPhone").value.trim();
            const type = document.getElementById("complaintType").value.trim();
            const details = document.getElementById("complaintDetails").value.trim();

            if (!name || !phone || !type || !details) {
                formMessage.textContent = "Kripya sabhi details bhariyega.";
                return;
            }

            const complaintItem = document.createElement("article");
            complaintItem.className = "complaint-item reveal-visible";
            complaintItem.innerHTML = `
                <div>
                    <h3>${type} Complaint - ${name}</h3>
                    <p>${details} | Mobile: ${phone}</p>
                </div>
                <span class="badge badge-live">New</span>
            `;

            complaintList.prepend(complaintItem);
            complaintForm.reset();
            formMessage.textContent = "Complaint safalta se submit ho gayi hai.";
        });
    }

    let activeFilter = "all";

    const applyDirectoryFilter = () => {
        const searchTerm = directorySearch ? directorySearch.value.trim().toLowerCase() : "";

        directoryCards.forEach((card) => {
            const category = card.dataset.category || "";
            const text = card.textContent.toLowerCase();
            const filterMatch = activeFilter === "all" || activeFilter === category;
            const searchMatch = text.includes(searchTerm);

            card.classList.toggle("hidden-card", !(filterMatch && searchMatch));
        });
    };

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            filterButtons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
            activeFilter = button.dataset.filter || "all";
            applyDirectoryFilter();
        });
    });

    if (directorySearch) {
        directorySearch.addEventListener("input", applyDirectoryFilter);
    }
});
