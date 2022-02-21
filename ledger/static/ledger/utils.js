dateTo_lt_dateFrom = (dateTo,dateFrom) => {
    let sliDateFrom = dateFrom.slice(-4) + dateFrom.slice(3,5) + dateFrom.slice(0,2)
    let sliDateTo =  dateTo.slice(-4) + dateTo.slice(3,5) + dateTo.slice(0,2)
    if (sliDateTo<sliDateFrom){
        return true
    } else{
        return false
    }
}