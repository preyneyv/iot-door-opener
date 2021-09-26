const _ = q => document.querySelector(q)
const ls = localStorage

let isOffline = false

// Register the cache service worker.
if ('serviceWorker' in navigator) {
    void navigator.serviceWorker.register('./cache.sw.js')
}

const API = {
    authHeader: token => ({'Authorization': `Bearer ${token}`}),
    defaultHeaders: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    async requestToken(password) {
        return fetch('/tokens/request', {
            method: 'POST',
            headers: {
                ...this.defaultHeaders
            },
            body: JSON.stringify({ password })
        })
    },
    async getTokenStatus() {
        return fetch('/tokens/status', {
            method: 'GET',
            headers: {
                ...this.defaultHeaders,
                ...this.authHeader(ls.statusToken)
            }
        })
    },
    async unlock() {
        return fetch('/door/unlock', {
            method: 'POST',
            headers: {
                ...this.defaultHeaders,
                ...this.authHeader(ls.accessToken)
            }
        })
    }
}


/**
 * Repeatedly confirm that we can contact the server. This will display a cover
 * screen if server connection fails.
 */
async function testServerConnection() {
    let timeout
    const status = await new Promise(resolve => {
        const img = new Image
        // console.log(img)
        img.onload = () => resolve(false)
        img.onerror = () => resolve(true)
        img.src = `/ping.gif?${Date.now()}`
        timeout = setTimeout(() => {
            resolve(true)
            img.src = ''
            window.stop()
        }, 1000)
    })
    clearTimeout(timeout)
    if (status !== isOffline) {
        // We just changed states!
        document.body.classList.toggle('offline', status)
        isOffline = status
    }
    setTimeout(testServerConnection, 1000)
}

void testServerConnection()

/**
 * A scene switching engine state machine. Used to keep track of which page
 * of the app we're on.
 */
class Engine {
    constructor(scenes, initial) {
        this.scenes = scenes
        this.active = initial
        scenes[initial].load()
    }

    switchTo(target, ...args) {
        const { active, scenes } = this
        if (target === active) {
            return console.warn(`Tried to switch to active scene ${target}!`)
        }
        scenes[active].unload()
        scenes[target].load(...args)
        this.active = target
        if ('activeElement' in document) {
            document.activeElement.blur()
        }
    }
}

/**
 * A parent class for all scenes. Used in tandem with the Engine.
 */
class Scene {
    constructor(selector) { this.container = _(selector) }
    load(...args) { this.container.classList.add('show') }
    unload() { this.container.classList.remove('show') }
}

const requestAccessScene = new class extends Scene {
    constructor() {
        super('#request-access')
        const passwordField = _("#request-access__password")
        _('#request-access__form').addEventListener('submit', async e => {
            e.preventDefault()
            if (isOffline) {
                return
            }

            const pwd = passwordField.value
            const response = await API.requestToken(pwd)
            if (!response.ok) {
                switch (response.status) {
                    case 401: // Unauthorized
                        alert('Incorrect password!')
                        break
                    default: // Unknown error :/
                        alert(`An unknown error occurred! Status: ${response.status}`)
                        console.error(response)
                }
                return
            }

            const { token, nicename } = await response.json()
            ls.statusToken = token
            ls.statusNicename = nicename

            engine.switchTo('awaiting')
        })
    }

    unload() {
        super.unload();
        _('#request-access__password').blur()
        _('#request-access__form input[type=submit]').blur()
    }
}

const awaitingApprovalScene = new class extends Scene {
    constructor() {
        super('#awaiting-approval')
        this.timeout = null
        this.checkStatus = this.checkStatus.bind(this)
    }

    async checkStatus() {
        if (isOffline) {
            return this.timeout = setTimeout(this.checkStatus, 1000)
        }

        let response
        try {
            response = await API.getTokenStatus()
        } catch (e) {
            return this.timeout = setTimeout(this.checkStatus, 1000)
        }

        if (!response.ok) {
            switch (response.status) {
                case 400:
                    alert('Request denied.')
                    ls.clear()
                    engine.switchTo('request')
                    break
                case 401:
                    alert(`An unexpected error occurred:\n` +
                          await response.text())
                    ls.clear()
                    engine.switchTo('request')
                    break
                default:
                    alert(`An unknown error occurred! Status: ${response.status}`)
                    console.error(response)
            }
            return
        }
        const { approved, token, name } = await response.json()
        if (approved) {
            ls.accessToken = token
            ls.unlockName = name

            engine.switchTo('unlock')
        } else {
            this.timeout = setTimeout(this.checkStatus, 1000)
        }
    }

    load() {
        super.load()
        _("#awaiting-approval__nicename").innerHTML = ls.statusNicename
        void this.checkStatus()
    }

    unload() {
        super.unload()

        clearTimeout(this.timeout)
        this.timeout = null
    }
}

const unlockScene = new class extends Scene {
    constructor() {
        super('#unlock')
        this.active = false
        this.button = _("#unlock__unlock")
        this.deauthorize = _("#unlock__deauthorize")
        this.checkbox = _("#unlock__automatic")

        this.triggerUnlock = this.triggerUnlock.bind(this)

        this.deauthorize.addEventListener('click', e => {
            e.preventDefault()
            if (!confirm("Are you sure? This means you'll need to get approved again!")) {
                return
            }
            ls.clear()
            engine.switchTo('request')
        })

        // Persist auto unlock preference
        this.checkbox.addEventListener('input', e => {
            ls.unlockAuto = e.target.checked
        })

        this.button.addEventListener('click', this.triggerUnlock)

        // Auto unlock if choice is selected and if the app gains focus and if
        // we're on this screen when that happens.
        window.addEventListener('focus', () => {
            if (this.active && ls.unlockAuto === 'true') {
                void this.triggerUnlock()
            }
        })
    }

    load() {
        super.load();
        this.active = true
        ls.statusToken = ''
        // Show the username
        _("#unlock__username").innerText = ls.unlockName

        // Restore auto unlock preference
        this.checkbox.checked = ls.unlockAuto === 'true'

        if (ls.unlockAuto === 'true') {
            void this.triggerUnlock()
        }
    }

    unload() {
        super.unload();
        this.active = false
    }

    async triggerUnlock() {
        if (isOffline) {
            return
        }
        this.button.disabled = true
        this.button.innerText = 'Unlocking...'
        const response = await API.unlock()
        if (!response.ok) {
            switch (response.status) {
                case 401:
                    alert(`An unexpected error occurred:\n` +
                          await response.text())
                    ls.clear()
                    engine.switchTo('request')
                    break
                default:
                    alert(`An unknown error occurred! Status: ${response.status}`)
                    console.error(response)
            }
            return
        }
        // Restore the button state, but only after a delay.
        // Unlocking is presumably going to be extremely quick and we want to
        // make sure we have enough visual feedback that the request was
        // accepted.
        setTimeout(() => {
            this.button.disabled = false
            this.button.innerText = 'Unlock'
        }, 500)
    }
}

let initialState = 'request'
if (ls.accessToken) {
    initialState = 'unlock'
} else if (ls.statusToken) {
    initialState = 'awaiting'
}

const engine = new Engine({
    request: requestAccessScene,
    awaiting: awaitingApprovalScene,
    unlock: unlockScene
}, initialState)
