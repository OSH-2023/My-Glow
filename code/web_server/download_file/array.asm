.data
led_data: .word 0x400
swt_data: .word 0x404
seg_rdv: .word 0x408
seg_data: .word 0x40C
swx_vld: .word 0x410
swx_data: .word 0x414
cnt_data: .word 0x418
mask: .word 0x80000000
num: .word 0x0

.text
addi s1,zero,1
lw a0,led_data
sw s1,(a0)

loop_1:
lw a2,swx_vld
lw s2,(a2)
beq s2,zero,loop_1
lw a3,swx_data
lw s6,(a3)            # s6=数组大小


addi s1,zero,2
lw a0,led_data
sw s1,(a0)

loop_2:
lw s2,(a2)
beq s2,zero,loop_2
lw s1,(a3)            # s1=数组首元素

sw s1,num,t1

addi t1,zero,3
lw a0,led_data
sw t1,(a0)
# ——————开始生成数组——————
# s6 = n
# s1 = 数组首元素
# s2 = 当前生成多少个元素
# s3 = 上一个元素
# s4 = 当前元素
# s5 = 当前元素地址
# t4 = mask
addi s2,zero,1
add s3,zero,s1
addi s4,zero,0
la s5,num
addi s5,s5,4
lw t4,mask

loop_3:
beq s2,s6,sort

slli t0,s3,1
and t0,t0,t4
slli t1,s3,2
and t1,t1,t4
slli t2,s3,22
and t2,t2,t4
and t5,s3,t4

add t3,t5,t0
add t3,t3,t1
add t3,t3,t2

and t3,t3,t4

srli s4,s3,1
or s4,s4,t3

sw s4,0(s5)
addi s2,s2,1
add s3,zero,s4
addi s4,zero,0
addi s5,s5,4
j loop_3

# ——————开始排序——————
# s3 = i
# s4 = j
# s5 = 数组元素首地址
# s6 = n
sort:
	lw a5,cnt_data
	lw s8,(a5)
	
	lw a6,seg_data
	sw s8,(a6)

	addi t1,zero,4
	lw a0,led_data
	sw t1,(a0)

      addi s3,zero,0     #i=0
      la   s5,num        
loop1:
      beq  s3,s6,check #i>=n
      addi s4,s3,-1    #else,j=i-1
loop2:
      blt  s4,zero,updatei #j<0,goto updatei
      slli t0,s4,2     #t0=j*4,word
      add  t0,s5,t0    #t0=num+j*4
      lw   t1,0(t0)    #t1=num[j]
      lw   t2,4(t0)    #t2=num[j+1]
      blt  t1,t2,updatei #if num[j]<=num[j+1].goto updatei
      mv   a0,s5       #else,a0=num, swap
      mv   a1,s4       #a1=j, swap
      jal  ra,swap
      addi s4,s4,-1    #j=j-1
      j    loop2
updatei:
      addi s3,s3,1     #i=i+1
      j    loop1

swap:
     slli t0,a1,2
     add  t0,a0,t0   #v+k
     lw   t1,0(t0)  #t1=v[k]
     lw   t2,4(t0)  #t2=v[k+1]
     sw   t2,0(t0)  #v[k]=t2
     sw   t1,4(t0)  #v[k+1]=t0
     jalr  x0,0(ra)

# ——————开始检测——————
check: 
	lw a5,cnt_data
	lw s9,(a5)
	lw a6,seg_data
	sw s9,(a6)
	
	addi t1,zero,5
	lw a0,led_data
	sw t1,(a0)
	
 	
	mv t0,s5
	addi a0,zero,0
	addi s6,s6,-1
loop3:
	beq a0,s6,done
	lw t1,0(t0)
	lw t2,4(t0)
	blt t2,t1,wrong
	addi t0,t0,4
	addi a0,a0,1
	jal loop3

done:
	addi s1, zero, 1
	j done
      
wrong:
	addi s1, zero, 0
	j wrong























  