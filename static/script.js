// =========================================================
// SEND MESSAGE
// =========================================================

async function sendMessage() {

    const input = document.getElementById("message-input")

    const chatBody = document.getElementById("chat-body")

    const message = input.value.trim()


    if (message === "") return


    // =====================================================
    // USER MESSAGE
    // =====================================================

    const userWrapper = document.createElement("div")

    userWrapper.className = "flex justify-end"


    userWrapper.innerHTML = `

        <div class="bg-black text-white px-4 py-3 rounded-2xl max-w-[80%] shadow-sm">

            ${message}

        </div>

    `


    chatBody.appendChild(userWrapper)

    input.value = ""

    chatBody.scrollTop = chatBody.scrollHeight


    // =====================================================
    // LOADING MESSAGE
    // =====================================================

    const loadingWrapper = document.createElement("div")

    loadingWrapper.className = "flex justify-start"

    loadingWrapper.id = "loading-message"


    loadingWrapper.innerHTML = `

        <div class="bg-white border px-4 py-3 rounded-2xl max-w-[80%] shadow-sm">

            Typing...

        </div>

    `


    chatBody.appendChild(loadingWrapper)

    chatBody.scrollTop = chatBody.scrollHeight


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message
            })
        })


        const data = await response.json()


        // =================================================
        // REMOVE LOADING
        // =================================================

        const loading = document.getElementById("loading-message")

        if (loading) {

            loading.remove()
        }


        // =================================================
        // BOT MESSAGE
        // =================================================

        const botWrapper = document.createElement("div")

        botWrapper.className = "flex justify-start"


        botWrapper.innerHTML = `

            <div class="bg-white border px-4 py-3 rounded-2xl max-w-[80%] shadow-sm">

                ${data.reply}

            </div>

        `


        chatBody.appendChild(botWrapper)

        chatBody.scrollTop = chatBody.scrollHeight


        // =================================================
        // IF DONE
        // =================================================

        if (data.done) {

            setTimeout(async () => {

                try {

                    await fetch("/reset", {

                        method: "POST"
                    })

                }

                catch(error) {

                    console.error(error)
                }

            }, 1500)
        }

    }

    catch(error) {

        console.error(error)


        const loading = document.getElementById("loading-message")

        if (loading) {

            loading.remove()
        }


        const errorWrapper = document.createElement("div")

        errorWrapper.className = "flex justify-start"


        errorWrapper.innerHTML = `

            <div class="bg-red-100 text-red-600 border border-red-300 px-4 py-3 rounded-2xl max-w-[80%] shadow-sm">

                Backend error occurred

            </div>

        `


        chatBody.appendChild(errorWrapper)

        chatBody.scrollTop = chatBody.scrollHeight
    }
}


// =========================================================
// CLOSE CHAT
// =========================================================

async function closeChat() {

    try {

        await fetch("/reset", {

            method: "POST"
        })

        window.location.href = "/"
    }

    catch(error) {

        console.error(error)
    }
}


// =========================================================
// ENTER KEY SUPPORT
// =========================================================

document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("message-input")

    input.addEventListener("keypress", function(event) {

        if (event.key === "Enter") {

            sendMessage()
        }
    })
})// =========================================================
// HELPERS
// =========================================================

const chatBody = () => document.getElementById("chat-body")
const msgInput = () => document.getElementById("message-input")
const sendBtn  = () => document.getElementById("send-btn")

function addMessage(text, sender) {
    const body    = chatBody()
    const wrapper = document.createElement("div")
    wrapper.className = sender === "user" ? "flex justify-end" : "flex justify-start"

    const bubble = document.createElement("div")
    bubble.className = sender === "user"
        ? "bg-black text-white px-4 py-3 rounded-2xl max-w-[80%] shadow-sm text-sm leading-relaxed"
        : "bg-white border px-4 py-3 rounded-2xl max-w-[80%] shadow-sm text-sm leading-relaxed"

    bubble.textContent = text
    wrapper.appendChild(bubble)
    body.appendChild(wrapper)
    body.scrollTop = body.scrollHeight
}

function showTyping() {
    const body    = chatBody()
    const wrapper = document.createElement("div")
    wrapper.className = "flex justify-start"
    wrapper.id = "typing-indicator"

    wrapper.innerHTML = `
        <div class="bg-white border px-4 py-3 rounded-2xl shadow-sm text-sm text-gray-400 flex gap-1 items-center">
            <span class="animate-bounce">●</span>
            <span class="animate-bounce" style="animation-delay:0.15s">●</span>
            <span class="animate-bounce" style="animation-delay:0.3s">●</span>
        </div>`

    body.appendChild(wrapper)
    body.scrollTop = body.scrollHeight
}

function removeTyping() {
    const el = document.getElementById("typing-indicator")
    if (el) el.remove()
}

function lockInput(locked) {
    msgInput().disabled = locked
    sendBtn().disabled  = locked
}


// =========================================================
// SEND MESSAGE
// =========================================================

async function sendMessage() {
    const input   = msgInput()
    const message = input.value.trim()
    if (!message) return

    addMessage(message, "user")
    input.value = ""
    lockInput(true)
    showTyping()

    try {
        const res  = await fetch("/chat", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ message })
        })

        const data = await res.json()
        removeTyping()
        addMessage(data.reply, "bot")

        if (data.done) {
            input.placeholder = "Form completed ✅"
            // reset after short delay so user reads final message
            setTimeout(async () => {
                await fetch("/reset", { method: "POST" })
            }, 2000)
        } else {
            lockInput(false)
            input.focus()
        }

    } catch (err) {
        removeTyping()
        addMessage("Network error. Please try again.", "bot")
        lockInput(false)
    }
}


// =========================================================
// CLOSE CHAT
// =========================================================

async function closeChat() {
    try {
        await fetch("/reset", { method: "POST" })
        window.location.href = "/"
    } catch (err) {
        console.error(err)
    }
}


// =========================================================
// ENTER KEY
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
    msgInput().addEventListener("keydown", e => {
        if (e.key === "Enter") {
            e.preventDefault()
            sendMessage()
        }
    })
})