extensions [ gis ]
globals [
  vegetation                ; input data of vegetation types for each patch
  tw-caught                 ; list of the weight of meat caught for each species
  tot_ht                    ; total time handling
  tot_st                    ; total time searching
  year day newday           ; counters for year, day and newday
  weight                    ; weight of animal for each species
  cumweight                 ; weight of caught animals cumulated over a year
  weightpd                  ; weight per day per hunter
  weightC0                  ; number of times a camp has no food
  success-rate              ; list of success rates for each species
  pursuit-time              ; list of pursuit rates for each species
  counted                   ; counter for the number of species checked in a patch during encounter procedure
  distcamp                  ; distance between hunter and camp
  meat_vt time_vt           ; for each vegetation type the weight of animals caught and time spend
  time-walk-cell            ; time spend in walking one patch
  tot-time-hunt             ; time spend on average a day on hunting
  capacity                  ; relative
  growthr                   ; annual growth rate of the population
  enc-dep                   ; encounter depression
  time                      ; time that has passed during a day
  avgweight                 ; average weight of meat per person per day over a whole year
  ssr1 ssr2 ssr6 ssr9 ssr11 ; success rate for cooperative hunting events
  pt1 pt2 pt6 pt9 pt11      ; pursuit time for cooperative hunting events
  groupsizecp               ; groupsize per cooperative hunting opportunity (except for armadillo's)
  groupsizea                ; groupsize per cooperative hunting opportunity for armadillo's
  nrhunterscreated           ; number of agents created in model
  rt-rate                   ; return rate for each species
  lost-opp                  ; number of times an encounter animal is not pursuit (list for each species)
  hunt-time                 ; time spend hunting different species
  arm-rad                   ; radius (in units of 100 meter) around encountered armadillo to recruit an additional hunter
  cells2                    ; fraction of an animal removed from landscape vegetation type 2 if we set encounter rate to zero of a particular species if an animal is killed
  cells3
  cells5
  cells7
  cells10
  cells12
  cells13
  ]
breed [hunters hunter]
breed [camps camp]
patches-own [
  vt               ; vegetation type
  encounter        ; encounter rates, which act as carrying capacity
  crowding         ; number of agents passing through cell during that day affecting the encounter rates
  caught           ; list of the number of animals for each species caught at the patch
  relencounter     ; relative population size
  relencounternew  ; new value after migration event
  ]
hunters-own [
  nrcaught         ; number of animals caught from each species
  pursuit          ; boolean whether agent is in pursuit
  campsite         ; camp of the agent
  done             ; done for the day
  nearest-neighbor ; nearest neighbor from the same camp
  time-hunt-budget ; time an agent has left to hunt
  time-hunted      ; time agent has hunted
  dailyweight      ; weight of animals caught by an agent
  potmeat          ; amount of meat caught during a pursuit
  pastdayrr        ; list of return rates during past days
  avgpastrr        ; average return rates over last x days
  time-pursuit     ; time an agent was in a pursuit
  ]
camps-own [
  nrmembers   ; number of members in a camp
  daycamp     ; number of days agents stay in the same camp
  directions  ; list of directions of initial movements at the start of the day
  directioncamp ; direction to which camp will move
  leftorright ; randomly defined boolean whether agents go initially left or right to the camp at the start of the day
  ]


; 0 - guan
; 1 - capuchin
; 2 - armadillo-s
; 3 - armadillo-b
; 4 - armadillo-t
; 5 - deer
; 6 - coati
; 7 - peccary-c
; 8 - lizard
; 9 - paca
; 10 - tapir
; 11 - peccary-wl
; 12 - Briku (briku/)
; 13 - jaku/
; 14 - kraja
; 15 - kryy
; 16 - kuchi
; 17 - nambu/
; 18 - aira
; 19 - ata
; 20 - chei
; 21 - krachova
; 22 - kuaremini
; 23 - tatukuju
; 24 - tayja
; 25 - tuka/

to setup
  __clear-all-and-reset-ticks
  ; import datasets
  set vegetation gis:load-dataset "../data/vegetation_100m.asc"
  ; apply encounter densities to patches
  gis:apply-raster vegetation vt

  ask patches [
    if vt = 2  [set encounter (list 0.0031 0.0016 0.0101 0.0062 0.0388 0.0008 0.0016 0.0000 0.0000 0.0039 0.0000 0.0008 0.00000 0.00155 0.00000 0.00000 0.00000 0.00000 0.00000 0.00000 0.00000 0.00000 0.00000 0.00078 0.00000 0.00000)]
    if vt = 3  [set encounter (list 0.0008 0.0108 0.0057 0.0037 0.0292 0.0008 0.0012 0.0003 0.0005 0.0008 0.0008 0.0023 0.00000 0.00092 0.00015 0.00000 0.00000 0.00062 0.00000 0.00000 0.00000 0.00000 0.00015 0.00000 0.00015 0.00000)]
    if vt = 5  [set encounter (list 0.0028 0.0072 0.0098 0.0041 0.0480 0.0003 0.0007 0.0011 0.0002 0.0029 0.0012 0.0023 0.00000 0.00064 0.00000 0.00000 0.00042 0.00021 0.00000 0.00000 0.00032 0.00000 0.00011 0.00011 0.00011 0.00000)]
    if vt = 7  [set encounter (list 0.0019 0.0082 0.0064 0.0031 0.0486 0.0014 0.0008 0.0005 0.0004 0.0022 0.0005 0.0023 0.00012 0.00065 0.00010 0.00017 0.00038 0.00012 0.00012 0.00021 0.00014 0.00005 0.00000 0.00000 0.00014 0.00000)]
    if vt = 10 [set encounter (list 0.0029 0.0050 0.0075 0.0035 0.0505 0.0006 0.0003 0.0002 0.0008 0.0024 0.0008 0.0041 0.00000 0.00000 0.00000 0.00000 0.00015 0.00000 0.00000 0.00000 0.00000 0.00000 0.00000 0.00000 0.00015 0.00000)]
    if vt = 12 [set encounter (list 0.0019 0.0065 0.0078 0.0041 0.0463 0.0009 0.0006 0.0003 0.0006 0.0029 0.0004 0.0022 0.00009 0.00074 0.00000 0.00003 0.00028 0.00003 0.00012 0.00003 0.00006 0.00000 0.00000 0.00000 0.00018 0.00003)]
    if vt = 13 [set encounter (list 0.0026 0.0094 0.0053 0.0030 0.0370 0.0011 0.0013 0.0001 0.0005 0.0005 0.0005 0.0033 0.00007 0.00112 0.00000 0.00007 0.00046 0.00020 0.00013 0.00000 0.00000 0.00000 0.00000 0.00007 0.00000 0.00000)]
  ]

  if scenario = "random-nocamp" [set nrcamps 0 set nrhunters 15 set flocking false set cooperativehunting false set probstraight 1]
  if scenario = "random-camp" [set nrcamps 3 set nrhunters 5 set flocking false set cooperativehunting false set probstraight 0.9]
  if scenario = "flocking" [set nrcamps 3 set nrhunters 5 set flocking true set cooperativehunting false set probstraight 0.9]
  if scenario = "flocking-coophunt" [set nrcamps 3 set nrhunters 5 set flocking true set cooperativehunting true set probstraight 0.9]

  ask patches
  [
    set crowding 0
    set enc-dep (list 0.6 0.1 0.8 0.9 0.6 0.4 0.1 0.4 0.9 0.8 0.4 0.1 0.6 0.6 0.1 0.8 0.6 0.6 0.6 0.6 0.9 0.4 0.8 0.8 0.6 0.6)
    set relencounter (list 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1)
    set relencounternew (list 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1)
    set caught (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    set groupsizecp (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    set groupsizea (list 0 0)
    viewupdate
  ]

  ; initialization parameters
  set year 0
  set day 0
  set rt-rate (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
  set lost-opp (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
  set hunt-time (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
  set cumweight 0
  set tw-caught (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
  set weightpd (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
  set tot_ht 0
  set tot_st 0

  set weight       (list 0.8    2.3  3.8   3.8  3.8   25.8 3.5   16.3 2.3  6.7   177  24.9  2.4  1.78   4   4.87  1.8 1.1    3.2  1   8   4.8 1.6 1.28  1.6  0.4)
  set pursuit-time (list 5      55   10     25   5     10   10    40   30   10    40   120   10   5      55  10    30  5      30   5   5   10  55  10    10   5)
  set success-rate (list 0.0625 0.7  0.276 0.33 0.032 0.18 0.643 0.26 0.61 0.106 0.05 0.192 0.05 0.0625 0.7 0.276 0.7 0.0625 0.25 0.1 0.8 0.1 0.7 0.276 0.05 0.03)
  set growthr      (list 0.15   0.14 0.69  0.69 0.69  0.4  0.23  0.84 0.1  0.67  0.2  1.25  0.15  0.15  0.17  0.39  1.1  0.15  0.28  11.51 0.1   0.23 0.48  0.69   0.15  0.15)

  set cells2       (list 0.1064 0.0686 0.4512 0.4512 0.4512 0.0247 0.3192 0.0000 0.0000 0.0928 0.0000 0.0078 0.0000 0.0301 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0301 0.0000 0.0000)
  set cells3       (list 0.0275 0.4630 0.2792 0.2792 0.2792 0.0247 0.2394 0.1076 0.0364 0.0190 0.0153 0.0223 0.0000 0.0179 0.0015 0.0000 0.0000 0.0109 0.0000 0.0000 0.0000 0.0000 0.0023 0.0000 0.0032 0.0000)
  set cells5       (list 0.0961 0.3086 0.4040 0.4040 0.4040 0.0093 0.1397 0.3944 0.0145 0.0690 0.0230 0.0223 0.0000 0.0124 0.0000 0.0000 0.0086 0.0037 0.0000 0.0000 0.0169 0.0000 0.0017 0.0042 0.0023 0.0000)
  set cells7       (list 0.0652 0.3515 0.3201 0.3201 0.3201 0.0432 0.1596 0.1793 0.0291 0.0524 0.0096 0.0223 0.0026 0.0126 0.0010 0.0091 0.0078 0.0021 0.0026 0.0036 0.0074 0.0011 0.0000 0.0000 0.0030 0.0000)
  set cells10      (list 0.0996 0.2143 0.3549 0.3549 0.3549 0.0185 0.0599 0.0717 0.0582 0.0571 0.0153 0.0398 0.0000 0.0000 0.0000 0.0000 0.0031 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0032 0.0000)
  set cells12      (list 0.0652 0.2786 0.3679 0.3679 0.3679 0.0278 0.1197 0.1076 0.0436 0.0690 0.0077 0.0214 0.0019 0.0144 0.0000 0.0016 0.0057 0.0005 0.0026 0.0005 0.0032 0.0000 0.0000 0.0000 0.0038 0.0007)
  set cells13      (list 0.0893 0.4030 0.2705 0.2705 0.2705 0.0340 0.2594 0.0359 0.0364 0.0119 0.0096 0.0320 0.0015 0.0217 0.0000 0.0037 0.0094 0.0035 0.0028 0.0000 0.0000 0.0000 0.0000 0.0027 0.0000 0.0000)

  let i 0
  while [i < nrspecies]
  [
     set rt-rate replace-item i rt-rate ((60 * item i success-rate * item i weight) / item i pursuit-time )
     set i i + 1
  ]

  ; success rates and pursuit times for cooperative hunting
  set ssr1 (list 0.7 0.4 0.304 0.260 0.238 0.226 0.221 0.221 0.224) ; total success rate capuchin monkey
  set ssr2 (list 0.276 0.216 0.196)
  set ssr6 (list 0.643 0.398 0.329 0.305 0.303 0.312 0.332 0.359 0.396); total success rate coati
  set ssr9 (list 0.106 0.163 0.210 0.252 0.289 0.324 0.357); total success rate paca
  set ssr11 (list 0.192 0.130 0.109 0.099 0.093 0.089 0.086 0.083 0.082 0.080); pecary wl

  set pt1 (list 55 40 40 50 60 80 100 135 185)
  set pt2 (list 10 5 5)
  set pt6 (list 10 10 10 10 10 20 25 35 55)
  set pt9 (list 15 15 20 20 25 30 30)
  set pt11 (list 120 75 60 55 55 55 60 60 65 75)


  set time-walk-cell 5
  set tot-time-hunt 355
  set arm-rad 1  ; radius for cooperative hunting for armadillos

  create-camps nrcamps
  [
    let found 0
    while [found = 0]
    [
       setxy random-xcor random-ycor
       if vt > 0 [set found 1]
    ]
    set shape "house"
    set color yellow
    set size 5
    set nrmembers 0
    set daycamp 0
    set hidden? false
  ]

  set nrhunterscreated 0
  set weightC0 0
  ifelse nrcamps > 0 [set nrhunterscreated nrhunters * nrcamps][set nrhunterscreated nrhunters]
  create-hunters nrhunterscreated
  [ set color blue
    set shape "person"
    set size 3
    set time 0
    set time-hunt-budget 355
    set dailyweight 0
    set nrcaught (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    set hidden? false
  ]
  ask hunters [
     let cx 0
     let cy 0
     let whichcamp 0
     set time-pursuit 0
     ifelse nrcamps > 0 [
       ask one-of camps with [nrmembers < nrhunters][set cx pxcor set cy pycor set whichcamp who set nrmembers nrmembers + 1]
     ][
       set whichcamp 0 - 1
       let found 0
       while [found < 1]
       [
         set cx random-pxcor
         set cy random-pycor
         if [vt] of patch cx cy > 0 [set found 1]
       ]
     ]
     set xcor cx
     set ycor cy
     set pastdayrr []
     set campsite whichcamp
     let j 0
     while [j < delaytime]
     [
       set pastdayrr lput 0.3 pastdayrr
       set j j + 1
     ]
  ]
  set newday 1
  let teller 0
  set meat_vt (list 0 0 0 0 0 0 0)
  set time_vt (list 0 0 0 0 0 0 0)
  set capacity 0
  ask patches with [vt > 0][set capacity capacity + mean relencounter]
  set capacity capacity / count patches with [vt > 0] ; average relencounter
end

to forage
  if newday = 1 [ ; define the location of the camp for the end of the day
    ask hunters [ ; initialize the variables of agents at the start of the day
      let i delaytime - 1
      let sumrr 0
      while [i > 0]
      [
        set pastdayrr replace-item i pastdayrr item (i - 1) pastdayrr
        set sumrr sumrr + item i pastdayrr
        set i i - 1
      ]
      ifelse time-pursuit > 0 [set pastdayrr replace-item 0 pastdayrr ((60 * dailyweight) / time-hunted)][set pastdayrr replace-item 0 pastdayrr 0]
      set sumrr sumrr + item 0 pastdayrr
      set avgpastrr sumrr / delaytime
      set dailyweight 0
      set time-pursuit 0
    ]
    set time 0
    ask hunters [set time-hunted 0]
    ask camps [
      ifelse daycamp = (daysincamp - 1) [
        set daycamp 0
        let found 0
        while [found = 0] ; test that the new position of the camp is still within the park.
        [
          lt random 360
          if patch-ahead 20 != nobody [; 20 is 2 km.
            if [vt] of patch-ahead 20 > 0 [fd 20 set xcor round xcor set ycor round ycor set found 1] ; Only when a valid position is found, where there is vegetation (vt > 0) a new position is determined
          ]
        ]
      ][
        set daycamp daycamp + 1
      ]
    ]
    ask patches [set crowding 0] ; initialize that agents have not passed through a cell at the beginning of the day
    set newday 0 ; the new day has started
    ask camps [
      if nrhunters = 1 [set directions (list 60)]
      if nrhunters = 2 [set directions (list 60 55)]
      if nrhunters = 3 [set directions (list 65 60 55)]
      if nrhunters = 4 [set directions (list 65 60 55 50)]
      if nrhunters = 5 [set directions (list 70 65 60 55 50)]
      if nrhunters = 6 [set directions (list 70 66 62 58 54 50)]
      if nrhunters = 7 [set directions (list 72 68 64 60 56 54 48)]
      if nrhunters = 8 [set directions (list 70 67 64 61 58 55 52 49)]
      if nrhunters = 9 [set directions (list 72 69 66 63 60 57 54 51 48)]
      if nrhunters = 10 [set directions (list 70 67.5 65 62.5 60 57.5 55 52.5 50 47.5)]
      if nrhunters = 15 [set directions (list 75 73 71 69 67 65 63 61 59 57 55 53 51 49 47)]
      if nrhunters = 20 [set directions (list 80 78 76 74 72 70 68 66 64 62 60 58 56 54 52 50 48 46 44 42)]
      set leftorright random 2
      set directioncamp random 360
    ]

    ask hunters [
      ifelse nrcamps > 0 [
        let mycampsite campsite
        ifelse [daycamp] of camp campsite > 0 [
        face camp campsite] ; the agents orient themself towards the camp site
        [set heading [directioncamp] of camp campsite]
        ifelse flocking [
          ifelse [leftorright] of camp campsite = 0 [
            let dir one-of [directions] of camp campsite
            rt dir
            ask one-of camps with [who = mycampsite][ set directions remove dir directions]
          ][
            let dir one-of [directions] of camp campsite
            lt dir
            ask one-of camps with [who = mycampsite][ set directions remove dir directions]
          ]
        ][
          ifelse random-float 1 < 0.5 [rt random 90][lt random 90] ; and then derive a direction from a 180 degree spectrum
        ]
      ][ ; if there is no camp agents move in a random direction
        set heading random 360
      ]
      let found 0 ; before an agent can make a step out of the camp, check whether this new position is still within the park
      while [found = 0]
      [
        if patch-ahead 1 != nobody [
           if [vt] of patch-ahead 1 > 0 [fd 1 set xcor round xcor set ycor round ycor set found 1] ; move when a valid position is found
        ]
        if found = 0 [rt random 90 lt random 90]
      ]
      set done 0
      set tot_st tot_st + time-walk-cell
      updatereturnrate time-walk-cell
    ]
    set time time + time-walk-cell ; update the time of the day
  ]
  ; end of initialization start of the day

  let allhuntersdone 0 ; this defines when all agents are back in the camp (allagentsdone = 1)
  while [allhuntersdone = 0]
  [
     ask hunters with [done = 0][
       ifelse pursuit <= 0 [
         ifelse nrcamps > 0 [
           set distcamp distance camp campsite
           set distcamp distcamp * time-walk-cell ; this is the expected time (in minutes) for an agent to walk back to the camp
         ][
           set distcamp 0
         ]
         ifelse time < (time-hunt-budget - distcamp) [ ; if there is still time for foraging
           caldirection
           encounterprocedure
         ][
           if distcamp > 0 [
             face camp campsite
             move
             encounterprocedure
           ]
         ]
       ][
         set pursuit pursuit - time-walk-cell
         if pursuit < 0 [set pursuit 0]
       ]
     ]
     set time time + time-walk-cell ; update time
     ask hunters with [done = 0][
       ifelse nrcamps > 0 [
         set distcamp distance camp campsite
       ][
         set distcamp 0
       ]
       if ((distcamp < 1) and (done = 0) and (nrcamps > 0)) or ((nrcamps = 0) and (time >= time-hunt-budget))[ ; is used to avoid numerical problems since agents may not reach exactly the home coordinates
         let i 0
         set done 1
         set time-hunted time
         while [i < nrspecies]
         [
           set tw-caught replace-item i tw-caught (item i tw-caught + item i nrcaught * item i weight)
           set i i + 1
         ]
         ; for each species the mean weight is added for each successful hunt
         updateweightlist
         let itemi dailyweight
         set cumweight cumweight + itemi
         set nrcaught (list 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
       ]
     ]
     if sum [done] of hunters = nrhunterscreated [
       set allhuntersdone 1
       if nrcamps > 0 [
         ask hunters [
           let selfcamp campsite
           set time-hunt-budget time-hunt-budget - (sum [time-hunted] of hunters with [campsite = selfcamp] / nrhunters) + tot-time-hunt
         ]
       ]
         ask camps [
           let selfcamp who
           let weightCC 0
           ask hunters with [campsite = selfcamp]
           [
             set weightCC weightCC + dailyweight
           ]
           set weightCC weightCC / nrhunters
           if weightCC < 0.001 [set weightC0 weightC0 + 1]
         ]
     ]
  ]
  set capacity 0
  ask patches with [vt > 0][set capacity capacity + mean relencounter]
  set capacity capacity / count patches with [vt > 0]
  tick
  set newday 1
  if day mod 92 = 0 [
    ask patches with [vt > 0][
      let ii 0
      while [ii < nrspecies]
      [
        set relencounternew replace-item ii relencounternew (0.5 * item ii relencounter + (0.5 * sum [item ii relencounter] of neighbors with [vt > 0]/ count neighbors with [vt > 0]))
        set ii ii + 1
      ]
    ]
    ask patches [set relencounter relencounternew]
  ]
  if day = 365 [
    ask patches [
      let ii 0
      while [ii < nrspecies]
      [
        set relencounter replace-item ii relencounter (item ii relencounter + ((item ii growthr * item ii relencounter) * (1 - (item ii relencounter))))
        if item ii relencounter < 0 [set relencounter replace-item ii relencounter 0]
        if item ii relencounter > 1 [set relencounter replace-item ii relencounter 1]
        set ii ii + 1
      ]
    ]
  ]
  ifelse day < 365 [set day day + 1][set avgweight (cumweight / (nrhunterscreated * 366))  set year year + 1 set day 0  set cumweight 0]
  if day = 0 [ ask patches [viewupdate]]

 if year = 100 [set cumweight cumweight / 366 stop]
end

; for each type of encounter we add the average time for each pursuit and the probability of a successful hunt (including the options of cooperative hunting)
to updatespecies [draw] ; for a given species
  if ((draw != 8) or (draw = 8 and day > 242)) [
    if random-float 1 < ((item draw encounter * item draw relencounter) * ( (item draw enc-dep) ^ ([crowding] of patch-here - 1))) [
      let exp-rt-rate item draw rt-rate
      let cnc 0 ; = 1 if a cooperative opportunity is ignored
      if cooperativehunting and (draw = 1 or draw = 2 or draw = 6 or draw = 9 or draw = 11)
      [
        let campself campsite
        let gs count hunters with [pursuit = 0 and campsite = campself] in-radius max-distance ; potential group size of cooperative hunt
        if draw = 1 [if length pt1 < gs [set gs length pt1]]
        if draw = 2 [if length pt2 < gs [set gs length pt2] if gs > 2 [set gs 2]]
        if draw = 6 [if length pt6 < gs [set gs length pt6]]
        if draw = 9 [if length pt9 < gs [set gs length pt9]]
        if draw = 11 [if length pt11 < gs [set gs length pt11]]
        if draw = 1 [set exp-rt-rate (((60 * item (gs - 1) ssr1 * gs * item draw weight) / (item (gs - 1) pt1)) / gs)]
        if draw = 2 [if gs > 1 [set exp-rt-rate (((60 * item 1 ssr2 * 2 * item draw weight) / (item 1 pt2)) / 2)]]
        if draw = 6 [set exp-rt-rate (((60 * item (gs - 1) ssr6 * gs * item draw weight) / (item (gs - 1) pt6)) / gs)]
        if draw = 9 [set exp-rt-rate (((60 * item (gs - 1) ssr9 * gs * item draw weight) / (item (gs - 1) pt9)) / gs)]
        if draw = 11 [set exp-rt-rate (((60 * item (gs - 1) ssr11 * gs * item draw weight) / (item (gs - 1) pt11)) / gs)]
        if gs > 1 and exp-rt-rate < avgpastrr [set cnc 1 set exp-rt-rate item draw rt-rate]
      ]
      let campself campsite
      ifelse exp-rt-rate >= avgpastrr * PN [ ; PN is pursuit or not. if PN is 0, agents will always pursuit
        let groupsize 0
        let hunterpx xcor
        let hunterpy ycor
        set campself campsite
        ask hunters [set potmeat 0]
        set counted 100
        ifelse cooperativehunting and (cnc = 0) and (draw = 1 or draw = 2 or draw = 6 or draw = 9 or draw = 11)
        [
          let patchhunt patch-here
          let target self
          set groupsize count hunters with [pursuit = 0 and campsite = campself] in-radius max-distance
          if draw = 1 [if length pt1 < groupsize [set groupsize length pt1]]
          if draw = 2 [if length pt2 < groupsize [set groupsize length pt2] if groupsize > 2 [set groupsize 2]]
          if draw = 6 [if length pt6 < groupsize [set groupsize length pt6]]
          if draw = 9 [if length pt9 < groupsize [set groupsize length pt9]]
          if draw = 11 [if length pt11 < groupsize [set groupsize length pt11]]
          let ssr 0 let pt 0
          if draw = 1 [
            ask n-of groupsize hunters with [pursuit = 0 and campsite = campself] in-radius max-distance [
              while [patch-here != patchhunt]
              [
                face target
                fd 1
                ask patch-here [set crowding crowding + 1]
              ]
              set xcor hunterpx
              set ycor hunterpy
            ]
            set ssr item (groupsize - 1) ssr1 * groupsize
            set pt item (groupsize - 1) pt1
          ]
          if draw = 2 [
            set groupsize 1
            set ssr item 0 ssr2
            set pt item 0 pt2
            if count hunters with [pursuit = 0 and campsite = campself] in-radius arm-rad > 1 [
              ask one-of hunters with [pursuit = 0 and campsite = campself] in-radius arm-rad [
                 while [patch-here != patchhunt]
                 [
                   face target
                   fd 1
                  ask patch-here [set crowding crowding + 1]
                 ]
                 set xcor hunterpx
                 set ycor hunterpy
              ]
              set ssr item 1 ssr2 * 2
              set pt item 1 pt2
              set groupsize 2
            ]
          ]
          if draw = 6 [
            ask n-of groupsize hunters with [pursuit = 0 and campsite = campself] in-radius max-distance [
              while [patch-here != patchhunt] [
                face target
                fd 1
                ask patch-here [set crowding crowding + 1]
              ]
              set xcor hunterpx
              set ycor hunterpy
            ]
            set ssr item (groupsize - 1) ssr6 * groupsize
            set pt item (groupsize - 1) pt6
          ]
          if draw = 9 [
            ask hunters with [pursuit = 0 and campsite = campself] in-radius max-distance [
              while [patch-here != patchhunt] [
                face target
                fd 1
                ask patch-here [set crowding crowding + 1]
              ]
              set xcor hunterpx
              set ycor hunterpy
            ]
            set ssr item (groupsize - 1) ssr9 * groupsize
            set pt item (groupsize - 1) pt9
          ]
          if draw = 11 [
            ask n-of groupsize hunters with [pursuit = 0 and campsite = campself] in-radius max-distance [
              while [patch-here != patchhunt] [
                face target
                fd 1
                ask patch-here [set crowding crowding + 1]
              ]
              set xcor hunterpx
              set ycor hunterpy
            ]
            set ssr item (groupsize - 1) ssr11 * groupsize
            set pt item (groupsize - 1) pt11
          ]
          ifelse draw = 2 [
            set groupsizea replace-item (groupsize - 1) groupsizea (item (groupsize - 1) groupsizea + 1)
          ][
            set groupsizecp replace-item (groupsize - 1) groupsizecp (item (groupsize - 1) groupsizecp + 1)
          ]
          ifelse draw = 2 [
            if groupsize = 2 [
              ask one-of other hunters with [pursuit = 0 and campsite = campself] in-radius arm-rad
              [
                set pursuit pt
                set tot_ht tot_ht + pt
                set time-pursuit time-pursuit + pt
                updatereturnrate pt
              ]
            ]
            set pursuit pt
            set tot_ht tot_ht + pt
            set time-pursuit time-pursuit + pt
            updatereturnrate pt
            set hunt-time replace-item 2 hunt-time (item 2 hunt-time + (2 * pt))
          ][
            ask n-of groupsize hunters with [pursuit = 0 and campsite = campself] in-radius max-distance
            [
              set pursuit pt
              set tot_ht tot_ht + pt
              set time-pursuit time-pursuit + pt
              updatereturnrate pt
            ]
            set hunt-time replace-item draw hunt-time (item draw hunt-time + (groupsize * pt))
          ]
          set ssr ssr / groupsize
          let nrcaughtcoop 0
          let ii 0
          while [ii < groupsize]
          [
            if random-float 1 < ssr [
              set nrcaught replace-item draw nrcaught ((item draw nrcaught) + 1)
              set nrcaughtcoop nrcaughtcoop + 1
              ask patch-here [set caught replace-item draw caught (item draw caught + 1)]
              set potmeat item draw weight
              updatemeat item draw weight
            ]
            set ii ii + 1
          ]
          if nrcaughtcoop > 0 [deplete draw nrcaughtcoop]
        ][
          set pursuit item draw pursuit-time
          set hunt-time replace-item draw hunt-time (item draw hunt-time + pursuit)
          set tot_ht tot_ht + item draw pursuit-time
          set time-pursuit time-pursuit + item draw pursuit-time
          updatereturnrate (item draw pursuit-time)
          if random-float 1 < item draw success-rate [
            set nrcaught replace-item draw nrcaught ((item draw nrcaught) + 1)
            ask patch-here [set caught replace-item draw caught (item draw caught + 1)]
            updatemeat item draw weight
            set potmeat item draw weight
            deplete draw 1
          ]
        ]
        ask hunters [set dailyweight dailyweight + potmeat]
      ][
        set lost-opp replace-item draw lost-opp (item draw lost-opp + 1)
      ]
    ]
  ]
end

to caldirection ; calculate the direction of the movement of the agents
  ifelse flocking [
    let mycampsite campsite
    set nearest-neighbor min-one-of other hunters with [campsite = mycampsite][distance myself]

    if nearest-neighbor != nobody [
       if time > 30 and distance nearest-neighbor < min-distance [ separate]] ; if after 30 minutes agents are less than half a cell near eachother they will adjust their direction to seperate


      ifelse random-float 1 < probstraight [ ; if agents go straight, there is a little noise added, and agents are adjusted (aligned) if other band members change directions.
        if wiggle > 0 [
          ifelse random 1 = 0 [rt random-float wiggle][lt random-float wiggle]
        ]
        align
        cohere
        move
        updatereturnrate time-walk-cell
      ][
        let currentheading heading ; if agent does not go straight it weights going to the direction of the camp versus continuing the current heading
        face camp campsite
        let campheading heading
        let degree 0
        if time-hunt-budget > 0 [set degree weightfactor * ticks / time-hunt-budget]
        if degree > 1 [set degree 1]
        ifelse (campheading > 180 and currentheading < 180) or (campheading < 180 and currentheading > 180) [
          if campheading > 180 [set campheading campheading - 180]
          if currentheading > 180 [set currentheading currentheading - 180]
        ][
          set heading degree * campheading + (1 - degree) * currentheading   ; redirect the heading balancing direction to camp and going forward
        ]

        align
        cohere
        move
        updatereturnrate time-walk-cell
      ]
  ][
    ifelse (random-float 1 < probstraight or ((scenario = "random-nocamp)" and ("brownianmotion" = false)))) [ ; with 90% chance go straight. But if an agent has encountered twice in a row a cell where other agents have been, redirect
      move ; agents walks one cell
      updatereturnrate time-walk-cell
    ][
      if nrcamps > 0 [
        let degree 0
        if time-hunt-budget > 0 [set degree weightfactor * ticks / time-hunt-budget]
        if degree > 1 [set degree 1]
        ifelse random-float 1 < degree [face camp campsite][rt 45 lt 45]
      ]
      if ((scenario = "random-nocamp") and ("brownianmotion" = true)) [rt random 360]
      move
      updatereturnrate time-walk-cell
    ]
  ]
end

to updatereturnrate [tim]
  if [vt] of patch-here = 2 [set time_vt replace-item 0 time_vt (item 0 time_vt + tim)]
  if [vt] of patch-here = 3 [set time_vt replace-item 1 time_vt (item 1 time_vt + tim)]
  if [vt] of patch-here = 5 [set time_vt replace-item 2 time_vt (item 2 time_vt + tim)]
  if [vt] of patch-here = 7 [set time_vt replace-item 3 time_vt (item 3 time_vt + tim)]
  if [vt] of patch-here = 10 [set time_vt replace-item 4 time_vt (item 4 time_vt + tim)]
  if [vt] of patch-here = 12 [set time_vt replace-item 5 time_vt (item 5 time_vt + tim)]
  if [vt] of patch-here = 13 [set time_vt replace-item 6 time_vt (item 6 time_vt + tim)]
end

to updatemeat [kg]
  if [vt] of patch-here = 2 [set meat_vt replace-item 0 meat_vt (item 0 meat_vt + kg)]
  if [vt] of patch-here = 3 [set meat_vt replace-item 1 meat_vt (item 1 meat_vt + kg)]
  if [vt] of patch-here = 5 [set meat_vt replace-item 2 meat_vt (item 2 meat_vt + kg)]
  if [vt] of patch-here = 7 [set meat_vt replace-item 3 meat_vt (item 3 meat_vt + kg)]
  if [vt] of patch-here = 10 [set meat_vt replace-item 4 meat_vt (item 4 meat_vt + kg)]
  if [vt] of patch-here = 12 [set meat_vt replace-item 5 meat_vt (item 5 meat_vt + kg)]
  if [vt] of patch-here = 13 [set meat_vt replace-item 6 meat_vt (item 6 meat_vt + kg)]
end

to move
  let found 0
  while [found = 0]
  [
    if patch-ahead 1 != nobody [
      if [vt] of patch-ahead 1 > 0 [fd 1 set xcor round xcor set ycor round ycor set found 1]
    ]
    if found = 0 [rt random 45 lt random 45]
   ]
   set tot_st tot_st + time-walk-cell
   ask patch-here [set crowding crowding + 1]
end

to updateweightlist
    if dailyweight < 0.1 [set weightpd replace-item 0 weightpd (item 0 weightpd + 1)]
    if (dailyweight >= 0.1 and dailyweight < 2) [set weightpd replace-item 1 weightpd (item 1 weightpd + 1)]
    if (dailyweight >= 2 and dailyweight < 4) [set weightpd replace-item 2 weightpd (item 2 weightpd + 1)]
    if (dailyweight >= 4 and dailyweight < 8) [set weightpd replace-item 3 weightpd (item 3 weightpd + 1)]
    if (dailyweight >= 8 and dailyweight < 16) [set weightpd replace-item 4 weightpd (item 4 weightpd + 1)]
    if (dailyweight >= 16 and dailyweight < 32) [set weightpd replace-item 5 weightpd (item 5 weightpd + 1)]
    if (dailyweight >= 32 and dailyweight < 64) [set weightpd replace-item 6 weightpd (item 6 weightpd + 1)]
    if (dailyweight >= 64 and dailyweight < 128) [set weightpd replace-item 7 weightpd (item 7 weightpd + 1)]
    if (dailyweight >= 128 and dailyweight < 256) [set weightpd replace-item 8 weightpd (item 8 weightpd + 1)]
    if dailyweight >= 256 [set weightpd replace-item 9 weightpd (item 9 weightpd + 1)]
end

to separate  ;; turtle procedure
  turn-away ([heading] of nearest-neighbor) max-separate-turn
end

to turn-away [new-heading max-turn]  ;; turtle procedure
  turn-at-most (subtract-headings heading new-heading) max-turn
end

to align  ;; turtle procedure
  turn-towards average-hunter-heading max-align-turn
end

to-report average-hunter-heading  ;; turtle procedure
  let campself campsite
  let x-component sum [dx] of other hunters with [campsite = campself]
  let y-component sum [dy] of other hunters with [campsite = campself]
  ifelse x-component = 0 and y-component = 0
    [ report heading ]
    [ report atan x-component y-component ]
end

to turn-towards [new-heading max-turn]  ;; turtle procedure
  turn-at-most (subtract-headings new-heading heading) max-turn
end

to turn-at-most [turn max-turn]  ;; turtle procedure
  ifelse abs turn > max-turn
    [ ifelse turn > 0
        [ rt max-turn ]
        [ lt max-turn ] ]
    [ rt turn ]
end

to deplete [drawn nrc] ; remove an animal from the landscape by putting the right number of encounter rates to zero
  if depletion [
    let removedanimal 0
    ask patch-here [set relencounter replace-item drawn relencounter 0
      if vt = 2 [set removedanimal removedanimal + item drawn cells2]
      if vt = 3 [set removedanimal removedanimal + item drawn cells3]
      if vt = 5 [set removedanimal removedanimal + item drawn cells5]
      if vt = 7 [set removedanimal removedanimal + item drawn cells7]
      if vt = 10 [set removedanimal removedanimal + item drawn cells10]
      if vt = 12 [set removedanimal removedanimal + item drawn cells12]
      if vt = 13 [set removedanimal removedanimal + item drawn cells13]

      if drawn = 2 or drawn = 3 or drawn = 4 [
         set relencounter replace-item 2 relencounter 0
         set relencounter replace-item 3 relencounter 0
         set relencounter replace-item 4 relencounter 0
    ]]


    let radiusnr 1
    while [removedanimal < 1] ; nr cells are cleared
    [
      let totteller count patches in-radius radiusnr with [item drawn relencounter > 0]
      let teller2 0
      while [(teller2 < totteller) and (removedanimal < 1)]
      [
        ask patches in-radius radiusnr [
          if item drawn relencounter > 0 [
            set relencounter replace-item drawn relencounter 0
            if vt = 2 [set removedanimal removedanimal + item drawn cells2]
            if vt = 3 [set removedanimal removedanimal + item drawn cells3]
            if vt = 5 [set removedanimal removedanimal + item drawn cells5]
            if vt = 7 [set removedanimal removedanimal + item drawn cells7]
            if vt = 10 [set removedanimal removedanimal + item drawn cells10]
            if vt = 12 [set removedanimal removedanimal + item drawn cells12]
            if vt = 13 [set removedanimal removedanimal + item drawn cells13]
            if drawn = 2 or drawn = 3 or drawn = 4 [
              set relencounter replace-item 2 relencounter 0
              set relencounter replace-item 3 relencounter 0
              set relencounter replace-item 4 relencounter 0
            ]
            set teller2 teller2 + 1
          ]
        ]
      ]
      set radiusnr radiusnr + 1
    ]
  ]
end

to cohere  ;; turtle procedure
  turn-towards average-heading-towards-flockmates max-cohere-turn
end

to-report average-heading-towards-flockmates
  let campself campsite
  let patchself patch-here
  let x-component 0
  let y-component 0
  let g 0
  ask other hunters with [campsite = campself]
  [
    if patch-here != patchself [
      set x-component sin (towards myself + 180)
      set y-component cos (towards myself + 180)
      set g g + 1
    ]
  ]
  if g > 0 [set x-component x-component / g set y-component y-component / g]
  ifelse x-component = 0 and y-component = 0
    [ report heading ]
    [ report atan x-component y-component ]
end

to-report wiggle
 ifelse nrcamps > 0 [
   let campself campsite
   let xcora xcor
   let ycora ycor
   let a-xcor 0
   let a-ycor 0
   ask hunters with [campsite = campself]
   [
     set a-ycor a-ycor + ycor
     set a-xcor a-xcor + xcor
   ]
   set a-ycor a-ycor / nrhunters
   set a-xcor a-xcor / nrhunters
   let distnodecamp 0
   let distaveragecamp 0
   ask camps with [who = campself]
   [
     set distnodecamp distancexy xcora ycora
     set distaveragecamp distancexy a-xcor a-ycor
   ]
   let distclosest 0
   let x 0
   ifelse distnodecamp < distaveragecamp [
     set nearest-neighbor min-one-of other hunters with [campsite = campself][distance myself]
     set distclosest distance nearest-neighbor
     set x 20 * distclosest
     if x < 0 [set x 0]
   ][
     set x 0
   ]
   report x
 ][
   report 0
 ]
end

to encounterprocedure ; check whether a species is encountered
  if [vt] of patch-here > 0 [ ;just to make sure that we are on a cell of the park
    let species []
    let ii 0
    while [ii < nrspecies]  ; define list of species
    [
      set species lput ii species
      set ii ii + 1
    ]
    set counted 0
    while [counted < nrspecies] ; we go randomly through the species list and stop if we encounter an animal of a species
    [
      let draw one-of species
      updatespecies draw
      set species remove draw species
      set counted counted + 1
    ]
  ]
end

to viewupdate
  if view = "landcover" [
    if vt = 0 [set pcolor black] ; no data
    if vt = 2 [set pcolor white] ; meadow / grassland
    if vt = 3 [set pcolor orange] ; bamboo
    if vt = 5 [set pcolor blue] ; riparian
    if vt = 7 [set pcolor green] ; high forest
    if vt = 10 [set pcolor 67] ; low forest
    if vt = 12 [set pcolor pink] ; bamboo understory
    if vt = 13 [set pcolor yellow] ; liana forest
  ]
  if view = "relative encounter" [if vt > 0 [set pcolor scale-color green mean relencounter 0 1]]
end
@#$#@#$#@
GRAPHICS-WINDOW
286
10
619
488
-1
-1
1.5
1
6
1
1
1
0
0
0
1
-108
108
-156
156
0
0
1
ticks
30.0

BUTTON
6
10
117
43
NIL
setup\n
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
6
43
117
76
NIL
forage
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

PLOT
626
10
1026
204
harvest
NIL
NIL
0.0
10.0
0.0
1.0
true
true
"" ""
PENS
"guan" 1.0 1 -7500403 true "" "plot-pen-reset\nset-plot-pen-color gray\nif ticks > 18300 [plot item 0 tw-caught / (ticks - 18300)]\nset-plot-pen-color red\nif ticks > 18300 [plot item 1 tw-caught / (ticks - 18300)]\nset-plot-pen-color orange\nif ticks > 18300 [plot (item 2 tw-caught + item 3 tw-caught + item 4 tw-caught) / (ticks - 18300)]\nset-plot-pen-color green\nif ticks > 18300 [plot item 5 tw-caught / (ticks - 18300)]\nset-plot-pen-color lime\nif ticks > 18300 [plot item 6 tw-caught / (ticks - 18300)]\nset-plot-pen-color turquoise\nif ticks > 18300 [plot item 7 tw-caught / (ticks - 18300)]\nset-plot-pen-color cyan\nif ticks > 18300 [plot item 8 tw-caught / (ticks - 18300)]\nset-plot-pen-color sky\nif ticks > 18300 [plot item 9 tw-caught / (ticks - 18300)]\nset-plot-pen-color blue\nif ticks > 18300 [plot item 10 tw-caught / (ticks - 18300)]\nset-plot-pen-color violet\nif ticks > 18300 [plot item 11 tw-caught / (ticks - 18300)]\nset-plot-pen-color gray"
"capuchin" 1.0 0 -2674135 true "" ""
"armadillo" 1.0 0 -955883 true "" ""
"deer" 1.0 0 -10899396 true "" ""
"coati" 1.0 0 -13840069 true "" ""
"peccary-c" 1.0 0 -14835848 true "" ""
"lizard" 1.0 0 -11221820 true "" ""
"paca" 1.0 0 -13791810 true "" ""
"tapir" 1.0 0 -13345367 true "" ""
"peccary-wl" 1.0 0 -8630108 true "" ""

PLOT
916
202
1117
367
share of time searching
NIL
NIL
0.0
1.0
0.0
1.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 false "" "if ((tot_ht + tot_st) > 0) [plot tot_st / (tot_ht + tot_st)]"

MONITOR
144
11
201
56
NIL
year
17
1
11

MONITOR
201
11
258
56
NIL
day
17
1
11

SLIDER
-1
143
117
176
nrspecies
nrspecies
1
26
26.0
1
1
NIL
HORIZONTAL

SWITCH
118
76
283
109
depletion
depletion
0
1
-1000

PLOT
626
202
917
365
return rates
NIL
NIL
0.0
7.0
0.0
0.02
false
true
"" ""
PENS
"meadow" 1.0 1 -1 true "" "plot-pen-reset\nset-plot-pen-color green\nif ticks > 0 [if item 0 time_vt > 0 [plot (item 0 meat_vt / item 0 time_vt)]]\nset-plot-pen-color orange\nif ticks > 0 [if item 1 time_vt > 0 [plot (item 1 meat_vt / item 1 time_vt)]]\nset-plot-pen-color blue\nif ticks > 0 [if item 2 time_vt > 0 [plot (item 2 meat_vt / item 2 time_vt)]]\nset-plot-pen-color lime\nif ticks > 0 [if item 3 time_vt > 0 [plot (item 3 meat_vt / item 3 time_vt)]]\nset-plot-pen-color turquoise\nif ticks > 0 [if item 4 time_vt > 0 [plot (item 4 meat_vt / item 4 time_vt)]]\nset-plot-pen-color orange\nif ticks > 0 [if item 5 time_vt > 0 [plot (item 5 meat_vt / item 5 time_vt)]]\nset-plot-pen-color yellow\nif ticks > 0 [if item 6 time_vt > 0 [plot (item 6 meat_vt / item 6 time_vt)]]\nset-plot-pen-color green"
"bamboo" 1.0 0 -955883 true "" ""
"riparian" 1.0 0 -13345367 true "" ""
"high forest" 1.0 0 -10899396 true "" ""
"low forest" 1.0 0 -8330359 true "" ""
"bamboo us" 1.0 0 -2064490 true "" ""
"liana forest" 1.0 0 -1184463 true "" ""

CHOOSER
139
465
287
510
view
view
"landcover" "relative encounter"
1

PLOT
-2
176
284
378
Relative encounter rates
NIL
NIL
0.0
1.0
0.0
1.0
true
false
"" ""
PENS
"average" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot capacity]"
"1" 1.0 0 -7500403 true "" "if ticks > 0 and day = 0 [plot mean ([item 0 relencounter]) of patches with [vt > 0]]"
"2" 1.0 0 -2674135 true "" "if ticks > 0 and day = 0 [plot mean ([item 1 relencounter]) of patches with [vt > 0]]"
"3" 1.0 0 -955883 true "" "if ticks > 0 and day = 0 [plot (mean ([item 2 relencounter]) of patches with [vt > 0] + mean ([item 3 relencounter]) of patches with [vt > 0] + mean ([item 4 relencounter]) of patches with [vt > 0]) / 3]"
"4" 1.0 0 -6459832 true "" "if ticks > 0 and day = 0 [plot mean ([item 5 relencounter]) of patches with [vt > 0]]"
"5" 1.0 0 -1184463 true "" "if ticks > 0 and day = 0 [plot mean ([item 6 relencounter]) of patches with [vt > 0]]"
"6" 1.0 0 -10899396 true "" "if ticks > 0 and day = 0 [plot mean ([item 7 relencounter]) of patches with [vt > 0]]"
"7" 1.0 0 -13840069 true "" "if ticks > 0 and day = 0 [plot mean ([item 8 relencounter]) of patches with [vt > 0]]"
"8" 1.0 0 -14835848 true "" "if ticks > 0 and day = 0 [plot mean ([item 9 relencounter]) of patches with [vt > 0]]"
"9" 1.0 0 -11221820 true "" "if ticks > 0 and day = 0 [plot mean ([item 10 relencounter]) of patches with [vt > 0]]"
"10" 1.0 0 -13791810 true "" "if ticks > 0 and day = 0 [plot mean ([item 11 relencounter]) of patches with [vt > 0]]"
"11" 1.0 0 -13345367 true "" "if ticks > 0 and day = 0 [plot mean ([item 12 relencounter]) of patches with [vt > 0]]"
"12" 1.0 0 -8630108 true "" "if ticks > 0 and day = 0 [plot mean ([item 13 relencounter]) of patches with [vt > 0]]"
"13" 1.0 0 -5825686 true "" "if ticks > 0 and day = 0 [plot mean ([item 14 relencounter]) of patches with [vt > 0]]"
"14" 1.0 0 -2064490 true "" "if ticks > 0 and day = 0 [plot mean ([item 15 relencounter]) of patches with [vt > 0]]"
"15" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 16 relencounter]) of patches with [vt > 0]]"
"16" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 17 relencounter]) of patches with [vt > 0]]"
"17" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 18 relencounter]) of patches with [vt > 0]]"
"18" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 19 relencounter]) of patches with [vt > 0]]"
"19" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 20 relencounter]) of patches with [vt > 0]]"
"20" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 21 relencounter]) of patches with [vt > 0]]"
"21" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 22 relencounter]) of patches with [vt > 0]]"
"22" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 23 relencounter]) of patches with [vt > 0]]"
"23" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 24 relencounter]) of patches with [vt > 0]]"
"24" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot mean ([item 25 relencounter]) of patches with [vt > 0]]"

SLIDER
0
77
117
110
nrhunters
nrhunters
1
25
5.0
1
1
NIL
HORIZONTAL

SLIDER
0
110
117
143
nrcamps
nrcamps
0
5
3.0
1
1
NIL
HORIZONTAL

PLOT
1026
10
1286
204
average weight
NIL
NIL
0.0
10.0
0.0
2.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "if ticks > 0 and day = 0 [plot avgweight]"

PLOT
626
364
917
514
Distribution Meat per day
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 1 -16777216 true "" "plot-pen-reset\nset-plot-pen-color green\nif ticks > 0 [plot item 0 weightpd]\nif ticks > 0 [plot item 1 weightpd]\nif ticks > 0 [plot item 2 weightpd]\nif ticks > 0 [plot item 3 weightpd]\nif ticks > 0 [plot item 4 weightpd]\nif ticks > 0 [plot item 5 weightpd]\nif ticks > 0 [plot item 6 weightpd]\nif ticks > 0 [plot item 7 weightpd]\nif ticks > 0 [plot item 8 weightpd]\nif ticks > 0 [plot item 9 weightpd]\nif ticks > 0 [plot item 10 weightpd]\nif ticks > 0 [plot item 11 weightpd]\nif ticks > 0 [plot item 12 weightpd]\nif ticks > 0 [plot item 13 weightpd]\nif ticks > 0 [plot item 14 weightpd]"

SLIDER
917
366
1022
399
daysincamp
daysincamp
1
31
1.0
1
1
NIL
HORIZONTAL

SWITCH
117
144
283
177
flocking
flocking
0
1
-1000

SLIDER
915
432
1022
465
probstraight
probstraight
0
1
0.9
0.01
1
NIL
HORIZONTAL

SLIDER
1025
366
1167
399
max-separate-turn
max-separate-turn
0
10
2.0
0.1
1
NIL
HORIZONTAL

SLIDER
1025
398
1168
431
max-align-turn
max-align-turn
0
10
10.0
1
1
NIL
HORIZONTAL

SLIDER
0
478
137
511
weightfactor
weightfactor
0
10
0.5
0.1
1
NIL
HORIZONTAL

SWITCH
117
110
283
143
cooperativehunting
cooperativehunting
0
1
-1000

SLIDER
1
412
137
445
min-distance
min-distance
0
1
0.0
0.01
1
NIL
HORIZONTAL

PLOT
1116
203
1288
367
groupsize
NIL
NIL
0.0
4.0
0.0
4.0
true
false
"" ""
PENS
"default" 1.0 1 -16777216 true "" "plot-pen-reset\nset-plot-pen-color red\nif ticks > 0 [plot item 0 groupsizecp]\nif ticks > 0 [plot item 1 groupsizecp]\nif ticks > 0 [plot item 2 groupsizecp]\nif ticks > 0 [plot item 3 groupsizecp]\nif ticks > 0 [plot item 4 groupsizecp]"

SLIDER
1025
432
1168
465
max-cohere-turn
max-cohere-turn
0
10
10.0
1
1
NIL
HORIZONTAL

SLIDER
-1
445
136
478
max-distance
max-distance
0
10
0.0
1
1
NIL
HORIZONTAL

CHOOSER
138
419
286
464
scenario
scenario
"random-nocamp" "random-camp" "flocking" "flocking-coophunt" "flocking-coophunt1" "flocking-coophunt2" "flocking-coophunt3" "flocking-coophunt4" "flocking-coophunt5" "flocking-coophunt6" "flocking-coophunt7" "flocking-coophunt8" "flocking-coophunt9" "flocking-coophunt15"
3

SLIDER
917
399
1023
432
delaytime
delaytime
0
40
20.0
1
1
NIL
HORIZONTAL

SWITCH
138
382
286
415
brownianmotion
brownianmotion
0
1
-1000

SLIDER
0
378
136
411
PN
PN
0
1
1.0
1
1
NIL
HORIZONTAL

@#$#@#$#@
This is a Netlogo implementation of hunting behavior of Ache hunter-gatherers based on ethnographic observations.


The model is implemented by Marco A. Janssen, Arizona State University in cooperation with Kim Hill, Arizona State University, August 2013.  

Copyright (C) 2013 K. Hill and M.A. Janssen

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.  
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.  
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.0.2
@#$#@#$#@
setup
display-cities
display-countries
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="experiment" repetitions="100" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>forage</go>
    <metric>item 0 tw-caught</metric>
    <metric>item 1 tw-caught</metric>
    <metric>item 2 tw-caught</metric>
    <metric>item 3 tw-caught</metric>
    <metric>item 4 tw-caught</metric>
    <metric>item 5 tw-caught</metric>
    <metric>item 6 tw-caught</metric>
    <metric>item 7 tw-caught</metric>
    <metric>item 8 tw-caught</metric>
    <metric>item 9 tw-caught</metric>
    <metric>item 10 tw-caught</metric>
    <metric>item 11 tw-caught</metric>
    <metric>item 12 tw-caught</metric>
    <metric>item 13 tw-caught</metric>
    <metric>item 14 tw-caught</metric>
    <metric>item 15 tw-caught</metric>
    <metric>item 16 tw-caught</metric>
    <metric>item 17 tw-caught</metric>
    <metric>item 18 tw-caught</metric>
    <metric>item 19 tw-caught</metric>
    <metric>item 20 tw-caught</metric>
    <metric>item 21 tw-caught</metric>
    <metric>item 22 tw-caught</metric>
    <metric>item 23 tw-caught</metric>
    <metric>item 24 tw-caught</metric>
    <metric>item 25 tw-caught</metric>
    <metric>tot_st</metric>
    <metric>tot_ht</metric>
    <metric>item 0 groupsizecp</metric>
    <metric>item 1 groupsizecp</metric>
    <metric>item 2 groupsizecp</metric>
    <metric>item 3 groupsizecp</metric>
    <metric>item 4 groupsizecp</metric>
    <metric>item 0 groupsizea</metric>
    <metric>item 1 groupsizea</metric>
    <metric>mean ([item 0 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 1 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>(mean ([item 2 relencounter] of patches with [vt &gt; 0]) + mean([item 3 relencounter] of patches with [vt &gt; 0]) + mean ([item 4 relencounter] of patches with [vt &gt; 0])) / 3</metric>
    <metric>mean ([item 5 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 6 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 7 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 8 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 9 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 10 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 11 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 12 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 13 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 14 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 15 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 16 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 17 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 18 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 19 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 20 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 21 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 22 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 23 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 24 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>mean ([item 25 relencounter]) of patches with [vt &gt; 0]</metric>
    <metric>item 0 time_vt</metric>
    <metric>item 1 time_vt</metric>
    <metric>item 2 time_vt</metric>
    <metric>item 3 time_vt</metric>
    <metric>item 4 time_vt</metric>
    <metric>item 5 time_vt</metric>
    <metric>item 6 time_vt</metric>
    <metric>item 0 meat_vt</metric>
    <metric>item 1 meat_vt</metric>
    <metric>item 2 meat_vt</metric>
    <metric>item 3 meat_vt</metric>
    <metric>item 4 meat_vt</metric>
    <metric>item 5 meat_vt</metric>
    <metric>item 6 meat_vt</metric>
    <metric>item 0 weightpd</metric>
    <metric>item 1 weightpd</metric>
    <metric>item 2 weightpd</metric>
    <metric>item 3 weightpd</metric>
    <metric>item 4 weightpd</metric>
    <metric>item 5 weightpd</metric>
    <metric>item 6 weightpd</metric>
    <metric>item 7 weightpd</metric>
    <metric>item 8 weightpd</metric>
    <metric>item 9 weightpd</metric>
    <metric>item 0 lost-opp</metric>
    <metric>item 1 lost-opp</metric>
    <metric>item 2 lost-opp</metric>
    <metric>item 3 lost-opp</metric>
    <metric>item 4 lost-opp</metric>
    <metric>item 5 lost-opp</metric>
    <metric>item 6 lost-opp</metric>
    <metric>item 7 lost-opp</metric>
    <metric>item 8 lost-opp</metric>
    <metric>item 9 lost-opp</metric>
    <metric>item 10 lost-opp</metric>
    <metric>item 11 lost-opp</metric>
    <metric>item 12 lost-opp</metric>
    <metric>item 13 lost-opp</metric>
    <metric>item 14 lost-opp</metric>
    <metric>item 15 lost-opp</metric>
    <metric>item 16 lost-opp</metric>
    <metric>item 17 lost-opp</metric>
    <metric>item 18 lost-opp</metric>
    <metric>item 19 lost-opp</metric>
    <metric>item 20 lost-opp</metric>
    <metric>item 21 lost-opp</metric>
    <metric>item 22 lost-opp</metric>
    <metric>item 23 lost-opp</metric>
    <metric>item 24 lost-opp</metric>
    <metric>item 25 lost-opp</metric>
    <metric>weightC0</metric>
    <metric>mean [time-hunt-budget] of agents</metric>
    <metric>item 0 hunt-time</metric>
    <metric>item 1 hunt-time</metric>
    <metric>item 2 hunt-time</metric>
    <metric>item 3 hunt-time</metric>
    <metric>item 4 hunt-time</metric>
    <metric>item 5 hunt-time</metric>
    <metric>item 6 hunt-time</metric>
    <metric>item 7 hunt-time</metric>
    <metric>item 8 hunt-time</metric>
    <metric>item 9 hunt-time</metric>
    <metric>item 10 hunt-time</metric>
    <metric>item 11 hunt-time</metric>
    <metric>item 12 hunt-time</metric>
    <metric>item 13 hunt-time</metric>
    <metric>item 14 hunt-time</metric>
    <metric>item 15 hunt-time</metric>
    <metric>item 16 hunt-time</metric>
    <metric>item 17 hunt-time</metric>
    <metric>item 18 hunt-time</metric>
    <metric>item 19 hunt-time</metric>
    <metric>item 20 hunt-time</metric>
    <metric>item 21 hunt-time</metric>
    <metric>item 22 hunt-time</metric>
    <metric>item 23 hunt-time</metric>
    <metric>item 24 hunt-time</metric>
    <metric>item 25 hunt-time</metric>
    <enumeratedValueSet variable="nragents">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="nrspecies">
      <value value="26"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="nrcamps">
      <value value="3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="depletion">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="daysincamp">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="view">
      <value value="&quot;relative encounter&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="cooperativehunting">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="probstraight">
      <value value="0.9"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-separate-turn">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-align-turn">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-cohere-turn">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="weightfactor">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="min-distance">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-distance">
      <value value="3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="scenario">
      <value value="&quot;flocking-coophunt&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="delaytime">
      <value value="20"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="PN">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="brownianmotion">
      <value value="true"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
