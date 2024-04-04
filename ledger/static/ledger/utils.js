//  

date1_lte_date2 = (date1,date2) => {
    let slidate2 = date2.slice(-4) + date2.slice(3,5) + date2.slice(0,2)
    let slidate1 =  date1.slice(-4) + date1.slice(3,5) + date1.slice(0,2)
    if (slidate1<=slidate2){
        return true
    } else{
        return false
    }
}

updateTabs = (dateFrom, dateTo, reimbursed, payed, outstanding) =>{
    let reimbursedTotal = 0
    let reimbursedContent = ''
    for (const [i, trans] of reimbursed.entries()){
        const transDate = trans.created_at
        if (date1_lte_date2(transDate,dateTo) && date1_lte_date2(dateFrom,transDate)){
            for (const each of trans.table_list){
                reimbursedTotal+= Number(each.amount)
                reimbursedContent+= 
                    `<tr class="transRow">
                        <td class="refCell">
                        </td>
                        <td class="dateCell">
                            ${transDate}
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
            }
        }
    }
    reimbursedContent +=
        `<tr>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="text-end fw-bold">Total</td>
            <td class="text-end fw-bold">${reimbursedTotal.toFixed(2)}</td>
        </tr>`
    $('#reimbursedBody').html(reimbursedContent)

    let payedContent = ''
    let payedTotal=0
    for (const [i, trans] of payed.entries()){
        const transDate = trans.created_at
        if (date1_lte_date2(transDate,dateTo) && date1_lte_date2(dateFrom,transDate)){
            for (const [j,each] of trans.table_list.entries()){
                let voucherNo = '';
                if (j==0){
                    voucherNo = `PV${trans.voucher_no}`;
                }
                payedTotal+= Number(each.amount)
                payedContent+= 
                    `<tr class="transRow" data-id='${trans.id}'>
                        <td class="refCell">
                            ${voucherNo}
                        </td>
                        <td class="dateCell">
                            ${transDate}
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
            }
        }
    }
    payedContent +=
        `<tr>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="text-end fw-bold">Total</td>
            <td class="text-end fw-bold">${payedTotal.toFixed(2)}</td>
        </tr>`
    $('#totalPayedBody').html(payedContent)

    let outstandingContent = ''
    let outstandingTotal=0
    if (outstanding.length>0){
        for (const [i, trans] of outstanding.entries()){
            const transDate = trans.created_at
            if (date1_lte_date2(transDate,dateTo) && date1_lte_date2(dateFrom,transDate)){
                for (const [j,each] of trans.table_list.entries()){
                    let voucherNo = '';
                    let resolveBtnHTML = '';
                    if (j==0){
                        voucherNo = `PV${trans.voucher_no}`;
                        resolveBtnHTML = `<a data-id='${trans.id}' class="btn btn-outline-success py-0 resolveBtn" href='../${trans.id}/resolve-adat/' >yes</a>`;
                    }
                    outstandingTotal+= Number(each.amount)
                    outstandingContent+= 
                        `<tr class="transRow" data-id='${trans.id}'>
                            <td class="refCell">
                                ${voucherNo}
                            </td>
                            <td class="dateCell">
                                ${transDate}
                            </td>
                            <td>${trans.category}</td>
                            <td>
                                ${each.description}
                            </td>
                            <td>
                                ${trans.receiver}
                            </td>
                            <td class="text-end">${each.amount}</td>
                            <td class="text-center">${resolveBtnHTML}</td>
                        </tr>`        
                }
            }
        }
    }
    
    outstandingContent +=
        `<tr>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="text-end fw-bold">Total</td>
            <td class="text-end fw-bold">${outstandingTotal.toFixed(2)}</td>
            <td></td>
        </tr>`
    $('#outstandingBody').html(outstandingContent)
}