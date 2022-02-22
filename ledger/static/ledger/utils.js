date1_lt_date2 = (date1,date2) => {
    let slidate2 = date2.slice(-4) + date2.slice(3,5) + date2.slice(0,2)
    let slidate1 =  date1.slice(-4) + date1.slice(3,5) + date1.slice(0,2)
    if (slidate1<slidate2){
        return true
    } else{
        return false
    }
}

updateTabs = (dateFrom, dateTo, reimbursed,) =>{
    let reimbursedTotal = 0
    for (const [i, trans] of reimbursed.entries()){
        if (!date1_lt_date2(trans.created_at,dateFrom) && date1_lt_date2())
        for (const each of trans.table_list){
            reimbursedTotal+= Number(each.amount)
            $('#reimbursedBody').append(
                `<tr class="transRow">
                <td class="refCell">
                </td>
                <td class="dateCell">
                    ${trans.created_at}
                </td>
                <td>${trans.category}</td>
                <td>
                    ${each.description}
                </td>
                <td>
                    ${trans.receiver}
                </td>
                <td class="text-end">${each.amount}</td>
            </tr>`
            )
        }
    }
    $('#reimbursedBody').append(`
        <tr>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="text-end fw-bold">Total</td>
            <td class="text-end fw-bold">${reimbursedTotal.toFixed(2)}</td>
        </tr>
    `)
}