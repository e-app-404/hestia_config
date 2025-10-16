# Sensors Table

| room               | motion                            | occupancy                            | presence                            | illuminance                    | counts              |
| ------------------ | --------------------------------- | ------------------------------------ | ----------------------------------- | ------------------------------ | ------------------- |
| bedroom            | bin*s.bedroom_motion*β            | bin*s.bedroom_occupancy*β            | bin*s.bedroom_presence*β            | sens.bedroom*illuminance*β     | m:6 o:4 p:2 i:2 x:2 |
| ensuite            | bin*s.ensuite_motion*β            | bin*s.ensuite_occupancy*β            | bin*s.ensuite_presence*β            | sens.ensuite*illuminance*β     | m:2 o:3 p:2 i:2 x:0 |
| desk               | bin_s.desk_motion_proxy           | bin*s.desk_occupancy*β               | bin*s.desk_presence*β               | null                           | m:1 o:2 p:3 i:0 x:2 |
| kitchen            | bin*s.kitchen_motion*β            | bin*s.kitchen_occupancy*β            | bin*s.kitchen_presence*β            | null                           | m:2 o:3 p:1 i:0 x:0 |
| living_room        | bin*s.living_room_motion*β        | bin*s.living_room_occupancy*β        | bin*s.living_room_presence*β        | sens.living*room_illuminance*β | m:2 o:2 p:2 i:2 x:0 |
| hallway_downstairs | bin*s.hallway_downstairs_motion*β | bin*s.hallway_downstairs_occupancy*β | bin*s.hallway_downstairs_presence*β | null                           | m:3 o:2 p:1 i:0 x:1 |
| hallway_upstairs   | bin*s.hallway_upstairs_motion*β   | bin*s.hallway_upstairs_occupancy*β   | bin*s.hallway_upstairs_presence*β   | null                           | m:2 o:2 p:1 i:0 x:0 |
