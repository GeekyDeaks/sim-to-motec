// simple script to download and process the GPS co-ords from viper4r's repo
// and generate a JSON file for usage in python

const https = require('https')
const vm = require('vm')
const fs = require('fs/promises')

const BASE_URL = "https://raw.githubusercontent.com/eckhchri/pcars-ds-liveview/master/"
const FILES = [
    "RefPoint.js",
    "RefPointData.js",
    "RefPointDataAMS2.js"
]

// get the list of tracks and their IDs from the dedicated server API
// curl http://127.0.0.1:9000/api/list/tracks > stm/ams2/tracks/list.json
const API_TRACKS_LIST = "stm/ams2/tracks/list.json"
const GPS_TRACKS_LIST = "stm/ams2/tracks/gps.json"

async function download(url, dest) {

    return new Promise( (resolve, reject) => {
        let request = https.get(url, function(res) {
            let data = ''
            res.on('data', chunk => data += chunk )
            res.on('end', () => resolve(data))
            res.on('error', reject)
        })
    })

}

async function run(files) {

    let track_json = await fs.readFile(API_TRACKS_LIST, 'utf8')
    let api_tracks = JSON.parse(track_json)
    let tracks = api_tracks.response.list
    // download and parse each of the classes
    for(let f of files) {
        console.log(f)
        let url = `${BASE_URL}${f}`
        console.log(url)
        let code = await download(url)
        console.log(`size = ${code.length}`)
        vm.runInThisContext(code)
    }

    let { refPoints } = new RefPointDataAMS2()

    // loop through each track

    let gpstracks = []

    let elements = ['refLat', 'refLong', 'rotation', 'cor_PosX_mul', 'cor_PosY_mul'];

    tracks.forEach( t => {
        let gps = { trackVariation: t.name }
        for(let e of elements) {
            let rp = refPoints[t.id]
            if(!rp) continue
            gps[e] = rp[e]
        }
        gpstracks.push(gps)
    })

    await fs.writeFile(GPS_TRACKS_LIST, JSON.stringify(gpstracks, null, 2))

}

run(FILES)