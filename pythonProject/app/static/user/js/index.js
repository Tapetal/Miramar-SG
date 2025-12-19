const menuBtn = document.getElementById("menu-btn");
const navLinks = document.getElementById("nav-links");
const menuBtnIcon = menuBtn.querySelector("i");

menuBtn.addEventListener("click", () => {
  navLinks.classList.toggle("open");

  const isOpen = navLinks.classList.contains("open");
  menuBtnIcon.setAttribute("class", isOpen ? "ri-close-line" : "ri-menu-line");
});

navLinks.addEventListener("click", () => {
  navLinks.classList.remove("open");
  menuBtnIcon.setAttribute("class", "ri-menu-line");
});

const scrollRevealOption = {
  distance: "50px",
  origin: "bottom",
  duration: 1000,
};

// header container
ScrollReveal().reveal(".header__container p", {
  ...scrollRevealOption,
});

ScrollReveal().reveal(".header__container h1", {
  ...scrollRevealOption,
  delay: 500,
});

// about container
ScrollReveal().reveal(".about__image img", {
  ...scrollRevealOption,
  origin: "left",
});

ScrollReveal().reveal(".about__content .section__subheader", {
  ...scrollRevealOption,
  delay: 500,
});

ScrollReveal().reveal(".about__content .section__header", {
  ...scrollRevealOption,
  delay: 1000,
});

ScrollReveal().reveal(".about__content .section__description", {
  ...scrollRevealOption,
  delay: 1500,
});

ScrollReveal().reveal(".about__btn", {
  ...scrollRevealOption,
  delay: 2000,
});

// room container
ScrollReveal().reveal(".room__card", {
  ...scrollRevealOption,
  interval: 500,
});

// service container
ScrollReveal().reveal(".service__list li", {
  ...scrollRevealOption,
  interval: 500,
  origin: "right",
});


document.addEventListener("DOMContentLoaded", function () {
    const profileImage = document.getElementById("profileImage");
    const profileDropdown = document.getElementById("profileDropdown");

    profileImage.addEventListener("click", function () {
        if (profileDropdown.style.display === "flex") {
            profileDropdown.style.display = "none";
        } else {
            profileDropdown.style.display = "flex";
            profileDropdown.style.opacity = "1";
        }
    });

    // Optional: Click outside to close the dropdown
    document.addEventListener("click", function (event) {
        if (!profileImage.contains(event.target) && !profileDropdown.contains(event.target)) {
            profileDropdown.style.display = "none";
        }
    });
});

// Booking form validation
const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    const checkInInput = document.getElementById('check-in');
    const checkOutInput = document.getElementById('check-out');
    const guestsInput = document.getElementById('guests');
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    checkInInput.setAttribute('min', today);
    checkOutInput.setAttribute('min', today);
    
    // Update checkout minimum when check-in changes
    checkInInput.addEventListener('change', function() {
        checkOutInput.setAttribute('min', this.value);
        if (checkOutInput.value && checkOutInput.value <= this.value) {
            checkOutInput.value = '';
        }
    });
    
    bookingForm.addEventListener('submit', function(e) {
        const checkIn = new Date(checkInInput.value);
        const checkOut = new Date(checkOutInput.value);
        const guests = parseInt(guestsInput.value);
        
        if (checkOut <= checkIn) {
            e.preventDefault();
            alert('Check-out date must be after check-in date!');
            return false;
        }
        
        if (guests < 1) {
            e.preventDefault();
            alert('Please enter a valid number of guests!');
            return false;
        }
    });
}
