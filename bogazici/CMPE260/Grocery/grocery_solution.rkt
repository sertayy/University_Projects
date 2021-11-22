#lang scheme
;2016400075

(define(HELPER_FUNC farm list)

  (if(eqv? (length list) 0) 0
     (if(equal? farm (caar list))
        (cadar list)
        (HELPER_FUNC farm (cdr list))))
  )

(define (TRANSPORTATION-COST farm)

  (HELPER_FUNC farm FARMS)
  )     

(define(HELPER_FUNC_2 farm list)

  (if(eqv? (length list) 0) '()
     (if(equal? farm (caar list))
        (caddar list)
        (HELPER_FUNC_2 farm (cdr list))))
  )

(define (AVAILABLE-CROPS farm)

  (HELPER_FUNC_2 farm FARMS)
  )

(define(HELPER_FUNC_3 customer list)

  (if(eqv? (length list) 0) '()
     (if(equal? customer (caar list))
        (caddar list)
        (HELPER_FUNC_3 customer (cdr list))))
  )

(define (INTERESTED-CROPS customer)

  (HELPER_FUNC_3 customer CUSTOMERS)
  )

(define(HELPER_FUNC_4 customer list)

  (if(eqv? (length list) 0) '()
     (if(equal? customer (caar list))
        (cadar list)
        (HELPER_FUNC_4 customer (cdr list))))
  )

(define (CONTRACT-FARMS customer)

  (HELPER_FUNC_4 customer CUSTOMERS)
  )

(define (CONTRACT-WITH-FARM_helper2 farm cfarmlist2 customs )

  (if(eqv? (length cfarmlist2) 0) null
     (if(equal? farm (car cfarmlist2))
        (list (caar customs))
        (CONTRACT-WITH-FARM_helper2 farm (cdr cfarmlist2) customs)))
  )

(define (CONTRACT-WITH-FARM_helper clist farm)

  (if(eqv? (length clist) 0) null
     (append (CONTRACT-WITH-FARM_helper2 farm (CONTRACT-FARMS (caar clist)) clist) (CONTRACT-WITH-FARM_helper (cdr clist) farm)))
  )

(define (CONTRACT-WITH-FARM farm)

  (CONTRACT-WITH-FARM_helper CUSTOMERS farm)
  )

(define (INTERESTED-IN-CROP_helper2 crop ccroplist2 customs )

  (if(eqv? (length ccroplist2) 0) null
     (if(equal? crop (car ccroplist2))
        (list (caar customs))
        (INTERESTED-IN-CROP_helper2 crop (cdr ccroplist2) customs)))
  )

(define (INTERESTED-IN-CROP_helper clist crop)

  (if(eqv? (length clist) 0) null
     (append (INTERESTED-IN-CROP_helper2 crop (INTERESTED-CROPS (caar clist)) clist) (INTERESTED-IN-CROP_helper (cdr clist) crop)))

  )

(define (INTERESTED-IN-CROP crop)

  (INTERESTED-IN-CROP_helper CUSTOMERS crop)
  )

(define (MIN-SALE-PRICE_helper crlist crop)

  (if(eqv? (length crlist) 0) null
     (if(equal? crop (caar crlist))
        (append (list (caddar crlist)) (MIN-SALE-PRICE_helper (cdr crlist) crop))
        (MIN-SALE-PRICE_helper (cdr crlist) crop)))
  )

(define (CROP-LIST crops)

  (if(eqv? (length crops) 0) null (append(list (caar crops)) (CROP-LIST (cdr crops))))
  )

(define (member? u lst)

  (not (equal? (member u lst) #f))
  )

(define (MIN-SALE-PRICE crop)

  (if(member? crop (CROP-LIST CROPS)) (car(sort (MIN-SALE-PRICE_helper CROPS crop) <)) 0)
  )

(define (CROPS-BETWEEN_helper2 min max crops)

  (define (f x) (and (<= x max) (>= x min)) )
  (if(eqv? (length crops) 0) null
     (if(equal? (f (caddar crops)) #t)
        (append (list(caar crops)) (CROPS-BETWEEN_helper2 min max (cdr crops)))
        (CROPS-BETWEEN_helper2 min max (cdr crops))))
  )

(define (removed2 lst)

  (cond ((empty? lst) empty)
        ((not (member? (first lst) (rest lst)))
        (cons (first lst) (removed2 (rest lst))))
        (else (removed2 (rest lst))))
  )

(define (CROPS-BETWEEN min max)
  
  (removed2(CROPS-BETWEEN_helper2 min max CROPS))
  )

(define (BUY-PRICE_helper3 customer transcost allcrops crop farm allfarms)

  (if(eqv? (length allcrops) 0)
     (BUY-PRICE_helper customer crop (cdr allfarms))
     (if(eqv? crop (caar allcrops))
        (if(eqv? farm (cadar allcrops))
           (sort(append (list (+ transcost (caddar allcrops))) (BUY-PRICE_helper customer crop (cdr allfarms)))<)
           (BUY-PRICE_helper3 customer transcost (cdr allcrops) crop farm allfarms))
        (BUY-PRICE_helper3 customer transcost (cdr allcrops) crop farm allfarms)))
  ) 

(define (BUY-PRICE_helper2 customer crop farmfeatures allfarms)

  (if(member? crop (caddr farmfeatures))
     (BUY-PRICE_helper3 customer (cadr farmfeatures) CROPS crop (car farmfeatures) allfarms)
     (BUY-PRICE_helper customer crop (cdr allfarms)))

  )

(define(BUY-PRICE_helper customer crop allfarms )

  (if(eqv? (length allfarms) 0)
     null (if(member? (caar allfarms) (CONTRACT-FARMS customer))
             (BUY-PRICE_helper2 customer crop (car allfarms) allfarms)
             (BUY-PRICE_helper customer crop (cdr allfarms))))
  )
  
(define (BUY-PRICE customer crop)
 
  (car(BUY-PRICE_helper customer crop FARMS))
  )

(define (TOTAL-PRICE_helper desiredcrops customer)
  
  (if(eqv? (length desiredcrops) 0) 0 (+(BUY-PRICE customer (car desiredcrops)) (TOTAL-PRICE_helper (cdr desiredcrops) customer)))
  )

(define (TOTAL-PRICE customer)
  
  (TOTAL-PRICE_helper (INTERESTED-CROPS customer) customer)
  )