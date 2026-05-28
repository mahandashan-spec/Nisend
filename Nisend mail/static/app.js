const passInp = document.querySelector("#password");
const repassInp = document.querySelector("#repassword");
const submitBTN = document.querySelector(".sub");
const username = document.querySelector(".username");
const mailInp = document.querySelector(".mail");

function checkValuidPass() {
    if (passInp.value.length < 8) {
        passInp.style.color = "red";
        return false;
    } else {
        passInp.style.color = "green";
        return true;
    }
}

function checkrepeat() {
    if (passInp.value === repassInp.value) {
        repassInp.style.color = "green";
        return true;
    } else {
        repassInp.style.color = "red";
        return false;
    }
}

function checkMail() {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@nisend\.com$/;

    if (emailPattern.test(mailInp.value)) {
        return true
    } else {
        alert("choose a mail with correct pattern");
        return false
    }
}



submitBTN.addEventListener("click", (e) => {
    e.preventDefault();
    const checkValuidPassResult = checkValuidPass();
    const checkrepeatResult = checkrepeat();
    const checkMailResult = checkMail();
    // spinner.classList.remove('d-none'); // نمایش لودر
    setTimeout(() => {
        if (username.value && checkValuidPassResult && checkrepeatResult && checkMailResult) {
            const data = {
                username: username.value,
                password: passInp.value,
                mail: mailInp.value
            };

            fetch('/mail/Register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    'username': username.value,
                    'password': passInp.value,
                    'mail': mailInp.value
                }).toString()
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = "/";
                        alert("Register succes!! login to your acount");
                    } else {
                        alert("faild: " + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("An error occurred.");
                });
        } else {
            console.log(false);
            alert("faild");
        }
    }, 1000);

});
