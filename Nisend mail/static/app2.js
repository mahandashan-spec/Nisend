const passInp = document.querySelector("#password");
const repassInp = document.querySelector("#repassword");
const submitBTN = document.querySelector(".sub");
const username = document.querySelector(".username");
var codeP = document.querySelector(".code");
var codeINP = document.querySelector(".inpCode");
var code;

document.addEventListener("DOMContentLoaded", () => {
    code = generateRandomString(5);
    codeP.textContent = code;
});

function generateRandomCharacter() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const randomIndex = Math.floor(Math.random() * characters.length);
    return characters.charAt(randomIndex);
}

function generateRandomString(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < length; i++) {
        result += generateRandomCharacter();
    }
    return result;
}

function checkValuidPass() {
    if (passInp.value.length < 8) {
        passInp.style.color = "red";
        return false;
    } else {
        passInp.style.color = "green";
        return true;
    }
}

function checkCode() {
    if (codeINP.value === code) {
        return true;
    } else {
        return false;
    }
}

submitBTN.addEventListener("click", (e) => {
    e.preventDefault();
    const checkValuidPassResult = checkValuidPass();
    const checkCodeResult = checkCode();
    const spinner = submitBTN.querySelector('.spinner-border');
    spinner.classList.remove('d-none'); // نمایش لودر

    setTimeout(() => {
        if (checkValuidPassResult && checkCodeResult && username.value) {
            fetch('/mail/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: 'username=' + username.value + '&password=' + passInp.value
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("log in successfully!!!")
                        window.location.href = "/";
                    } else {
                        alert("faild: " + data.message);
                    }
                });
        } else {
            alert("comppelate the form");
        }
    }, 1000);
})