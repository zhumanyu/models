#MobileNetV2_x0_25
python train.py \
       --model=MobileNetV2_x0_25 \
       --batch_size=256 \
       --total_images=1281167 \
       --class_dim=1000 \
       --image_shape=3,224,224 \
       --model_save_dir=output/ \
       --lr_strategy=cosine_decay \
       --num_epochs=240 \
       --lr=0.1 \
       --l2_decay=3e-5 \
       --lower_ratio=1.0 \
       --upper_ratio=1.0
