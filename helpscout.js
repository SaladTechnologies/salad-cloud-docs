!(function (e, t, n) {
    function a() {
        var e = t.getElementsByTagName('script')[0],
            n = t.createElement('script')
        ;(n.type = 'text/javascript'),
            (n.async = !0),
            (n.src = 'https://beacon-v2.helpscout.net'),
            e.parentNode.insertBefore(n, e)
    }
    if (
        ((e.Beacon = n =
            function (t, n, a) {
                e.Beacon.readyQueue.push({ method: t, options: n, data: a })
            }),
        (n.readyQueue = []),
        'complete' === t.readyState)
    )
        return a()
    e.attachEvent ? e.attachEvent('onload', a) : e.addEventListener('load', a, !1)
})(window, document, window.Beacon || function () {})
window.Beacon('init', '4f355e62-a67a-4f94-a807-d66284f35ea5')
