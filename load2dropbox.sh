source .env
DATE=`date +%Y-%m-%d`

echo $DATE >> "$LOGS_DIR/load.log"
echo "Loading to dropbox" >> "$PROJECT_DIR/$LOGS_DIR/load2dropbox_$DATE.log"

for file in `ls $DATA_DIR`
do
    echo "Loading $file" >> "$LOGS_DIR/load.log"
    NAME=`echo $file | sed 's/\..*//'`
    curl -X POST https://content.dropboxapi.com/2/files/upload \
        --header "Authorization: Bearer sl.Bi-R97n0n_w_84m6DQ8z08dfDN1f_hFzBtCbI-yNOlE2EUH_6-IMY9NNb2-e_xWkTr590DZXqvV1oQbQ3vzPHw_W-k-JnyMiB7toQl930rcVt9wSuOc_s0mmsyJt6wJdtTwS9t9x49ED" \
        --header "Dropbox-API-Arg: {\"path\": \"/$NAME$DATE.csv\"}" \
        --header "Content-Type: application/octet-stream" \
        --data-binary @$PROJECT_DIR/$DATA_DIR/$file >>"$LOGS_DIR/load.log"

done


    
    
    
    
    # --header "Dropbox-API-Arg: {\"path\": \"$DATA_DIR.MODAAPL.csv\"}" \