interface ShipInfo {
    x: number
    y: number
    cnt: number
    from_x: number
    from_y: number
    to_x: number
    to_y: number
    tooltip: string
    icon: string
    icon_selected: string
    ships: string[]
}

interface DateInfo {
    date: string
    map_id: string
    infos: ShipInfo[]
}

interface Result {
    name: string
    info: string
    visual_map: DateInfo[]
    gantt: any
    ships: string[]
}

interface Port {
    name: string
    x: number
    y: number
}

export type { ShipInfo, DateInfo, Result, Port }
