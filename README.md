# sensor_monitoring_docker

## What it does

### receive_can

canの通信を受け取ってlog dirに保存する．
また，gather_dataのserver側にtcp/ip通信で送信する．

#### can 設定

receive_can/code_rep/config.jsonに設定がある．

- can_channel

  pcに刺さっているusbのcan deviceのlink名．ip link等で確認できる．ここに登録されている全てのものについてcan device upを試みる．認識できない時，現状error終了する．

- range

  gachacon deviceのidの範囲を受け取る．start <= endが必要．

- check_data_received

  ここに登録されたデータは特別にhealth_checkに最後に受け取った時のtimestampが記録される．
  health_stateには影響しない．

- check_validation

  届いているか確認され，Trueの方の値を受信しているならばそのidにおけるhealth_stateはTrueである．
  それ以外についてはfalseである．

- send_check_valid

  基板の状態を確認するために送信するcanのdataである．check_validationが帰ってくることを想定している．

- intervals

  - can_send_period

    単位: seconds
    send_check_validをどの程度の頻度で送るか．

  - check_can_received

    単位: seconds
    check_validationにおけるheadについてどの程度の頻度で受信しているか確認する．

### gather_data

receive_canのtcp/ip通信を受け取りreceive_canと同様にlog dirに保存する．

## tcp/ip通信

host及びportの宣言は各moduleのcode_rep/config.jsonで行われている．
tcp_ip_infoのhost, portのところをgather_dataの動くpcのip address及び通信を受け取るportに設定する．
もし現状の2222 portから移したいときgather_data/docker_compose.ymlのports attributeについても書き換えることを推奨する．

## 保存先の説明

- log/health_check

  現在の基盤の状態および，最後に流れてきた通信の内容を記録している．

- log/log.txt

  can通信の生dataを保存している．
  保存形式はshellにおける`can dump`と同様である．
