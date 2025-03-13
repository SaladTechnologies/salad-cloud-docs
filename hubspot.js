const script = document.createElement('script')
script.type = 'text/javascript'
script.id = 'hs-script-loader'
script.async = true
script.defer = true
script.src = '//js.hs-scripts.com/7230102.js'

document.head.appendChild(script)

function trackUrlChanges() {
    let lastestPathname = window.location.pathname

    function handleUrlChange() {
        const _hsq = (window._hsq = window._hsq || [])
        const pathname = window.location.pathname

        if (pathname === lastestPathname) {
            return
        }

        lastestPathname = pathname
        _hsq.push(['setPath', pathname])
        _hsq.push(['trackPageView'])
    }

    // Observe title changes (indicating a new page load in SPAs)
    const observer = new MutationObserver(() => handleUrlChange())
    observer.observe(document.querySelector('title'), { childList: true })
}

trackUrlChanges()
