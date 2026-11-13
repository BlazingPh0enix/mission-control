# Delta-v map (KSP 1.x, m/s)

Transcribed from the community "Kerbal Space Program Δv Map" v1.7.3: map design by
/u/swashlebucky, atmospheric numbers by Kowgan, vacuum numbers by /u/CuriousMetaphor and
Armisael, original subway concept by /u/JellyCubes. Licensed CC BY-NC-SA 4.0.

All values are vacuum delta-v in m/s. Low orbits are 10 km above the atmosphere or the highest
terrain. Ascent values are typical; a better or worse ascent profile, TWR or aerodynamics changes
them. Totals don't include plane changes: each leg's text gives the largest plane change it may
need. Every landing mission below adds up to the total printed on the map.

`mission_budget` reads only the Legs and Missions tables. Leg ids must be unique and the dv column
must be a plain number.

## Reading the tables

- The map gives one value per leg, used in both directions: an ascent costs the same as the
  landing, and escaping a body costs the same as capturing into its low orbit.
- Coming home ends with `kerbin_aerobrake` (0 m/s): you arrive at Kerbin and aerobrake. The map
  marks every Kerbin-bound leg as aerobraking possible.
- Legs marked "aerobraking possible" can be partly or fully replaced by atmospheric drag. The
  "aerobraked" missions drop those legs; the map gives no figure for what is left, so keep a
  reserve for corrections and the final touchdown.
- Planets are reached from `kerbin_escape`, an elliptical orbit at the edge of Kerbin's sphere of
  influence (SOI). Moons of Eve, Duna and Jool are reached from the parent's elliptical orbit.
- Flight times use Kerbin's calendar (6-hour days, 426-day years) and are averages over ten
  years of launch windows.

## Bodies

| Body | Map total from Kerbin's surface (m/s) | Low orbit | Average flight time | Max plane change (m/s) | Atmosphere |
|---|---|---|---|---|---|
| Kerbin (keostationary orbit) | 4,515 | 80 km; keostationary at 2,863.33 km | | | Aerobraking, jet engines |
| Mun | 5,120 | 14 km | 8 hours | | |
| Minmus | 4,660 | 10 km | 56 hours | 340 | |
| Moho | 8,360 | 20 km | 100 days | 2,520 | |
| Eve | 13,800 | 100 km | 168 days | 430 | Aerobraking |
| Gilly | 5,000 | 10 km | via Eve | | |
| Duna | 6,520 | 60 km | 300 days | 10 | Aerobraking (thin) |
| Ike | 5,280 | 10 km | via Duna | | |
| Dres | 6,670 | 12 km | 1 year 171 days | 1,010 | |
| Jool | 22,250 | 210 km | 2 years 367 days | 270 | Aerobraking |
| Laythe | 10,190 | 60 km | via Jool | | Aerobraking, jet engines |
| Vall | 7,800 | 15 km | via Jool | | |
| Tylo | 9,190 | 10 km | via Jool | | |
| Bop | 6,810 | 30 km | via Jool | 2,440 | |
| Pol | 6,570 | 10 km | via Jool | 700 | |
| Eeloo | 7,460 | 10 km | 4 years 178 days | 1,330 | |
| Kerbol | 91,050 | 610 km | | | Aerobraking |

## Legs

### Kerbin

| id | leg | dv |
|---|---|---|
| kerbin_ascent | Kerbin surface to low Kerbin orbit (80 km) | 3400 |
| kso_transfer | Low Kerbin orbit to keostationary orbit (2,863.33 km), both burns | 1115 |
| kerbin_escape | Low Kerbin orbit to an elliptical orbit reaching Kerbin's SOI edge; every trip to another planet starts here | 930 |
| kerbin_aerobrake | Arrive at Kerbin and aerobrake to the surface; parachutes, plus a heat shield when returning from another planet | 0 |

### Mun

| id | leg | dv |
|---|---|---|
| mun_transfer | Low Kerbin orbit to a Mun intercept (about 8 hours) | 860 |
| mun_capture | Mun intercept to low Mun orbit (14 km) | 280 |
| mun_landing | Low Mun orbit to the Mun's surface | 580 |
| mun_ascent | Mun surface to low Mun orbit | 580 |
| mun_escape | Low Mun orbit onto a Kerbin return; aerobrake at Kerbin | 280 |

### Minmus

| id | leg | dv |
|---|---|---|
| minmus_transfer | Low Kerbin orbit to a Minmus intercept (about 56 hours), plus up to 340 for the plane change | 930 |
| minmus_capture | Minmus intercept to low Minmus orbit (10 km) | 150 |
| minmus_landing | Low Minmus orbit to Minmus's surface | 180 |
| minmus_ascent | Minmus surface to low Minmus orbit | 180 |
| minmus_escape | Low Minmus orbit onto a Kerbin return; aerobrake at Kerbin | 150 |

### Moho

| id | leg | dv |
|---|---|---|
| moho_transfer | Kerbin SOI edge to a Moho intercept (about 100 days), plus up to 2,520 for the plane change | 760 |
| moho_capture | Moho intercept to low Moho orbit (20 km) | 2400 |
| moho_landing | Low Moho orbit to Moho's surface | 870 |
| moho_ascent | Moho surface to low Moho orbit | 870 |
| moho_escape | Low Moho orbit onto a Kerbin transfer, plus up to 2,520 for the plane change; aerobrake at Kerbin | 2400 |

### Eve

| id | leg | dv |
|---|---|---|
| eve_transfer | Kerbin SOI edge to an Eve intercept (about 168 days), plus up to 430 for the plane change | 90 |
| eve_capture | Eve intercept to an elliptical Eve orbit (85 Mm by 100 km); aerobraking possible | 80 |
| eve_orbit | Elliptical Eve orbit to low Eve orbit (100 km); aerobraking possible | 1300 |
| eve_landing | Low Eve orbit to Eve's surface; aerobraking possible | 8000 |
| eve_aerobrake | Eve intercept to the surface by aerobraking, a heat shield and parachutes | 0 |
| eve_ascent | Eve surface to low Eve orbit, the hardest ascent in the game | 8000 |
| eve_orbit_raise | Low Eve orbit to the elliptical Eve orbit (85 Mm by 100 km) | 1300 |
| eve_escape | Elliptical Eve orbit onto a Kerbin transfer, plus up to 430 for the plane change; aerobrake at Kerbin | 80 |

### Gilly

| id | leg | dv |
|---|---|---|
| gilly_transfer | Elliptical Eve orbit to a Gilly intercept | 60 |
| gilly_capture | Gilly intercept to low Gilly orbit (10 km) | 410 |
| gilly_landing | Low Gilly orbit to Gilly's surface | 30 |
| gilly_ascent | Gilly surface to low Gilly orbit | 30 |
| gilly_escape | Low Gilly orbit to Gilly escape | 410 |
| gilly_departure | Gilly escape back to the elliptical Eve orbit | 60 |

### Duna

| id | leg | dv |
|---|---|---|
| duna_transfer | Kerbin SOI edge to a Duna intercept (about 300 days), plus up to 10 for the plane change | 130 |
| duna_capture | Duna intercept to an elliptical Duna orbit (48 Mm by 60 km); aerobraking possible | 250 |
| duna_orbit | Elliptical Duna orbit to low Duna orbit (60 km); aerobraking possible | 360 |
| duna_landing | Low Duna orbit to Duna's surface; aerobraking possible | 1450 |
| duna_aerobrake | Duna intercept to the surface by aerobraking and parachutes; Duna's air is thin, so keep a reserve for the final touchdown | 0 |
| duna_ascent | Duna surface to low Duna orbit | 1450 |
| duna_orbit_raise | Low Duna orbit to the elliptical Duna orbit (48 Mm by 60 km) | 360 |
| duna_escape | Elliptical Duna orbit onto a Kerbin transfer, plus up to 10 for the plane change; aerobrake at Kerbin | 250 |

### Ike

| id | leg | dv |
|---|---|---|
| ike_transfer | Elliptical Duna orbit to an Ike intercept | 30 |
| ike_capture | Ike intercept to low Ike orbit (10 km) | 150 |
| ike_landing | Low Ike orbit to Ike's surface | 390 |
| ike_ascent | Ike surface to low Ike orbit | 390 |
| ike_escape | Low Ike orbit to Ike escape | 150 |
| ike_departure | Ike escape back to the elliptical Duna orbit | 30 |

### Dres

| id | leg | dv |
|---|---|---|
| dres_transfer | Kerbin SOI edge to a Dres intercept (about 1 year 171 days), plus up to 1,010 for the plane change | 610 |
| dres_capture | Dres intercept to low Dres orbit (12 km) | 1300 |
| dres_landing | Low Dres orbit to Dres's surface | 430 |
| dres_ascent | Dres surface to low Dres orbit | 430 |
| dres_escape | Low Dres orbit onto a Kerbin transfer, plus up to 1,010 for the plane change; aerobrake at Kerbin | 1300 |

### Jool

| id | leg | dv |
|---|---|---|
| jool_transfer | Kerbin SOI edge to a Jool intercept (about 2 years 367 days), plus up to 270 for the plane change | 980 |
| jool_capture | Jool intercept to an elliptical Jool orbit (268 Mm by 210 km); aerobraking possible | 160 |
| jool_orbit | Elliptical Jool orbit to low Jool orbit (210 km); aerobraking possible | 2780 |
| jool_descent | Low Jool orbit to Jool's "surface"; Jool has none, so this is a one-way probe; aerobraking possible | 14000 |
| jool_escape | Elliptical Jool orbit onto a Kerbin transfer, plus up to 270 for the plane change; aerobrake at Kerbin | 160 |

### Laythe

| id | leg | dv |
|---|---|---|
| laythe_transfer | Elliptical Jool orbit to a Laythe intercept | 930 |
| laythe_capture | Laythe intercept to low Laythe orbit (60 km); aerobraking possible | 890 |
| laythe_landing | Low Laythe orbit to Laythe's surface; aerobraking possible | 2900 |
| laythe_aerobrake | Laythe intercept to the surface by aerobraking, a heat shield and parachutes | 0 |
| laythe_ascent | Laythe surface to low Laythe orbit; the air has oxygen, so jet engines can fly the first part | 2900 |
| laythe_escape | Low Laythe orbit to Laythe escape | 890 |
| laythe_departure | Laythe escape back to the elliptical Jool orbit | 930 |

### Vall

| id | leg | dv |
|---|---|---|
| vall_transfer | Elliptical Jool orbit to a Vall intercept | 620 |
| vall_capture | Vall intercept to low Vall orbit (15 km) | 850 |
| vall_landing | Low Vall orbit to Vall's surface | 860 |
| vall_ascent | Vall surface to low Vall orbit | 860 |
| vall_escape | Low Vall orbit to Vall escape | 850 |
| vall_departure | Vall escape back to the elliptical Jool orbit | 620 |

### Tylo

| id | leg | dv |
|---|---|---|
| tylo_transfer | Elliptical Jool orbit to a Tylo intercept | 400 |
| tylo_capture | Tylo intercept to low Tylo orbit (10 km) | 1050 |
| tylo_landing | Low Tylo orbit to Tylo's surface; no atmosphere, so all of it is powered | 2270 |
| tylo_ascent | Tylo surface to low Tylo orbit | 2270 |
| tylo_escape | Low Tylo orbit to Tylo escape | 1050 |
| tylo_departure | Tylo escape back to the elliptical Jool orbit | 400 |

### Bop

| id | leg | dv |
|---|---|---|
| bop_transfer | Elliptical Jool orbit to a Bop intercept, plus up to 2,440 for the plane change | 220 |
| bop_capture | Bop intercept to low Bop orbit (30 km) | 890 |
| bop_landing | Low Bop orbit to Bop's surface | 230 |
| bop_ascent | Bop surface to low Bop orbit | 230 |
| bop_escape | Low Bop orbit to Bop escape | 890 |
| bop_departure | Bop escape back to the elliptical Jool orbit, plus up to 2,440 for the plane change | 220 |

### Pol

| id | leg | dv |
|---|---|---|
| pol_transfer | Elliptical Jool orbit to a Pol intercept, plus up to 700 for the plane change | 160 |
| pol_capture | Pol intercept to low Pol orbit (10 km) | 810 |
| pol_landing | Low Pol orbit to Pol's surface | 130 |
| pol_ascent | Pol surface to low Pol orbit | 130 |
| pol_escape | Low Pol orbit to Pol escape | 810 |
| pol_departure | Pol escape back to the elliptical Jool orbit, plus up to 700 for the plane change | 160 |

### Eeloo

| id | leg | dv |
|---|---|---|
| eeloo_transfer | Kerbin SOI edge to an Eeloo intercept (about 4 years 178 days), plus up to 1,330 for the plane change | 1140 |
| eeloo_capture | Eeloo intercept to low Eeloo orbit (10 km) | 1370 |
| eeloo_landing | Low Eeloo orbit to Eeloo's surface | 620 |
| eeloo_ascent | Eeloo surface to low Eeloo orbit | 620 |
| eeloo_escape | Low Eeloo orbit onto a Kerbin transfer, plus up to 1,330 for the plane change; aerobrake at Kerbin | 1370 |

### Kerbol

The map rounds these three legs to the nearest 100, so they add up to 20 less than its Kerbol
total of 91,050.

| id | leg | dv |
|---|---|---|
| kerbol_transfer | Kerbin SOI edge to a solar orbit dipping to 610 km above Kerbol (13,600 Mm by 610 km) | 6000 |
| kerbol_orbit | That solar orbit to low Kerbol orbit (610 km); aerobraking possible | 13700 |
| kerbol_descent | Low Kerbol orbit to Kerbol's "surface"; Kerbol has none; aerobraking possible | 67000 |

## Missions

### Around Kerbin

| mission | legs |
|---|---|
| low kerbin orbit | kerbin_ascent |
| keostationary orbit | kerbin_ascent, kso_transfer |
| kerbin escape | kerbin_ascent, kerbin_escape |

### Mun

| mission | legs |
|---|---|
| mun flyby | kerbin_ascent, mun_transfer |
| mun orbit | kerbin_ascent, mun_transfer, mun_capture |
| mun orbit and return | kerbin_ascent, mun_transfer, mun_capture, mun_escape, kerbin_aerobrake |
| mun landing | kerbin_ascent, mun_transfer, mun_capture, mun_landing |
| mun landing and return | kerbin_ascent, mun_transfer, mun_capture, mun_landing, mun_ascent, mun_escape, kerbin_aerobrake |

### Minmus

| mission | legs |
|---|---|
| minmus flyby | kerbin_ascent, minmus_transfer |
| minmus orbit | kerbin_ascent, minmus_transfer, minmus_capture |
| minmus orbit and return | kerbin_ascent, minmus_transfer, minmus_capture, minmus_escape, kerbin_aerobrake |
| minmus landing | kerbin_ascent, minmus_transfer, minmus_capture, minmus_landing |
| minmus landing and return | kerbin_ascent, minmus_transfer, minmus_capture, minmus_landing, minmus_ascent, minmus_escape, kerbin_aerobrake |

### Moho

| mission | legs |
|---|---|
| moho flyby | kerbin_ascent, kerbin_escape, moho_transfer |
| moho orbit | kerbin_ascent, kerbin_escape, moho_transfer, moho_capture |
| moho landing | kerbin_ascent, kerbin_escape, moho_transfer, moho_capture, moho_landing |
| moho landing and return | kerbin_ascent, kerbin_escape, moho_transfer, moho_capture, moho_landing, moho_ascent, moho_escape, kerbin_aerobrake |

### Eve

| mission | legs |
|---|---|
| eve flyby | kerbin_ascent, kerbin_escape, eve_transfer |
| eve orbit | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, eve_orbit |
| eve landing | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, eve_orbit, eve_landing |
| eve aerobraked landing | kerbin_ascent, kerbin_escape, eve_transfer, eve_aerobrake |
| eve landing and return | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, eve_orbit, eve_landing, eve_ascent, eve_orbit_raise, eve_escape, kerbin_aerobrake |
| eve aerobraked landing and return | kerbin_ascent, kerbin_escape, eve_transfer, eve_aerobrake, eve_ascent, eve_orbit_raise, eve_escape, kerbin_aerobrake |

### Gilly

| mission | legs |
|---|---|
| gilly flyby | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, gilly_transfer |
| gilly orbit | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, gilly_transfer, gilly_capture |
| gilly landing | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, gilly_transfer, gilly_capture, gilly_landing |
| gilly landing and return | kerbin_ascent, kerbin_escape, eve_transfer, eve_capture, gilly_transfer, gilly_capture, gilly_landing, gilly_ascent, gilly_escape, gilly_departure, eve_escape, kerbin_aerobrake |

### Duna

| mission | legs |
|---|---|
| duna flyby | kerbin_ascent, kerbin_escape, duna_transfer |
| duna orbit | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, duna_orbit |
| duna landing | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, duna_orbit, duna_landing |
| duna aerobraked landing | kerbin_ascent, kerbin_escape, duna_transfer, duna_aerobrake |
| duna landing and return | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, duna_orbit, duna_landing, duna_ascent, duna_orbit_raise, duna_escape, kerbin_aerobrake |
| duna aerobraked landing and return | kerbin_ascent, kerbin_escape, duna_transfer, duna_aerobrake, duna_ascent, duna_orbit_raise, duna_escape, kerbin_aerobrake |

### Ike

| mission | legs |
|---|---|
| ike flyby | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, ike_transfer |
| ike orbit | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, ike_transfer, ike_capture |
| ike landing | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, ike_transfer, ike_capture, ike_landing |
| ike landing and return | kerbin_ascent, kerbin_escape, duna_transfer, duna_capture, ike_transfer, ike_capture, ike_landing, ike_ascent, ike_escape, ike_departure, duna_escape, kerbin_aerobrake |

### Dres

| mission | legs |
|---|---|
| dres flyby | kerbin_ascent, kerbin_escape, dres_transfer |
| dres orbit | kerbin_ascent, kerbin_escape, dres_transfer, dres_capture |
| dres landing | kerbin_ascent, kerbin_escape, dres_transfer, dres_capture, dres_landing |
| dres landing and return | kerbin_ascent, kerbin_escape, dres_transfer, dres_capture, dres_landing, dres_ascent, dres_escape, kerbin_aerobrake |

### Jool

| mission | legs |
|---|---|
| jool flyby | kerbin_ascent, kerbin_escape, jool_transfer |
| jool capture | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture |
| jool orbit | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, jool_orbit |
| jool descent | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, jool_orbit, jool_descent |

### Laythe

| mission | legs |
|---|---|
| laythe flyby | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, laythe_transfer |
| laythe orbit | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, laythe_transfer, laythe_capture |
| laythe landing | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, laythe_transfer, laythe_capture, laythe_landing |
| laythe aerobraked landing | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, laythe_transfer, laythe_aerobrake |
| laythe landing and return | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, laythe_transfer, laythe_capture, laythe_landing, laythe_ascent, laythe_escape, laythe_departure, jool_escape, kerbin_aerobrake |
| laythe aerobraked landing and return | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, laythe_transfer, laythe_aerobrake, laythe_ascent, laythe_escape, laythe_departure, jool_escape, kerbin_aerobrake |

### Vall

| mission | legs |
|---|---|
| vall flyby | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, vall_transfer |
| vall orbit | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, vall_transfer, vall_capture |
| vall landing | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, vall_transfer, vall_capture, vall_landing |
| vall landing and return | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, vall_transfer, vall_capture, vall_landing, vall_ascent, vall_escape, vall_departure, jool_escape, kerbin_aerobrake |

### Tylo

| mission | legs |
|---|---|
| tylo flyby | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, tylo_transfer |
| tylo orbit | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, tylo_transfer, tylo_capture |
| tylo landing | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, tylo_transfer, tylo_capture, tylo_landing |
| tylo landing and return | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, tylo_transfer, tylo_capture, tylo_landing, tylo_ascent, tylo_escape, tylo_departure, jool_escape, kerbin_aerobrake |

### Bop

| mission | legs |
|---|---|
| bop flyby | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, bop_transfer |
| bop orbit | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, bop_transfer, bop_capture |
| bop landing | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, bop_transfer, bop_capture, bop_landing |
| bop landing and return | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, bop_transfer, bop_capture, bop_landing, bop_ascent, bop_escape, bop_departure, jool_escape, kerbin_aerobrake |

### Pol

| mission | legs |
|---|---|
| pol flyby | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, pol_transfer |
| pol orbit | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, pol_transfer, pol_capture |
| pol landing | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, pol_transfer, pol_capture, pol_landing |
| pol landing and return | kerbin_ascent, kerbin_escape, jool_transfer, jool_capture, pol_transfer, pol_capture, pol_landing, pol_ascent, pol_escape, pol_departure, jool_escape, kerbin_aerobrake |

### Eeloo

| mission | legs |
|---|---|
| eeloo flyby | kerbin_ascent, kerbin_escape, eeloo_transfer |
| eeloo orbit | kerbin_ascent, kerbin_escape, eeloo_transfer, eeloo_capture |
| eeloo landing | kerbin_ascent, kerbin_escape, eeloo_transfer, eeloo_capture, eeloo_landing |
| eeloo landing and return | kerbin_ascent, kerbin_escape, eeloo_transfer, eeloo_capture, eeloo_landing, eeloo_ascent, eeloo_escape, kerbin_aerobrake |

### Kerbol

| mission | legs |
|---|---|
| kerbol low orbit | kerbin_ascent, kerbin_escape, kerbol_transfer, kerbol_orbit |
