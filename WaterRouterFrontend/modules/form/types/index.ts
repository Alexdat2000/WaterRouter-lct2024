interface Ship {
    name: string,
    from: string,
    to: string,
    date: string,
    speed: number,
    class: number,
}

interface Iceship {
    name: string,
    location: string,
    sp3: number,
    fine1: number,
    fine2: number,
}

interface Form {
    name: string,
    current_ships: Ship[],
    iceships: Iceship[],
    iceships_date: string,
    ships_filename: string,
    ice_filename: string,
}

export type { Ship, Iceship, Form }

