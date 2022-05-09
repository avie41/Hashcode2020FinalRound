## Stratégie 1
***Stratégie consistant à traiter les tâches ayant le plus gros ratio score 
/ longueur d'abord, et en plaçant le plus de robots possibles***

### Idées nécessaires à cette stratégies : 
* Il faut un algorithme capable de calculer la longueur du plus court chemin
passant par un ensemble de points donné.
* On cherche à distribuer dès le début le maximum de tâches. Cependant, si on se rends
compte qu'il est impossible de ditribuer une tâche, on la garde de côté en mode 
"tâche libre", et on y reviendra après si besoin.
* En cas de conflit avec un robot, un robot peut abandonner sa tâche et en choisir une 
autre si c'est plus court pour lui. La tâche abandonnée devient ainsi une tâche libre.

### Déroulé de l'algorithme :  

#### I. Calcul pour chaque tâche de leur ratio score / taille.
*Peut être à séparer en deux pour l'initialisation.* 
* Tant que toutes les tâches ne sont pas attribuées : 
    * On regarde de quel point de montage (tête de robot) la tâche est le plus proche (distance entre 
    le début de la tâche et le point de montage)
    * On place un robot sur ce point de montage et on lui attribue cette tâche.
    * Il est possible qu'à la dernière étape, il soit plus court de donner la tâche
    à un robot ayant déjà une tâche car la fin de la tâche du robot est proche du début
    de la tâche considérée. **Dans ce cas, et si le nombre total de mouvement autorisé
    n'est pas dépassé, on attribue une autre tâche au même robot.**
        * Si le nombre de mouvement est dépassé, on regarde un autre robot.
        * S'il n'y a pas d'autre robots, alors on laisse la tâche innocupée.
    * S'il n'y a plus de point de montage ou de robot disponible, ou si ajouter une tâche
    à un robot dépasse le nombre de mouvement autorisé, on sort de la boucle.
     
#### II. Avancée de chaque robot

* On fait évoluer mouvement par mouvement chaque robot. A chaque mouvement :
    * On recalcule le chemin à parcourir en fonction de la position des autres robots
    et de leurs bras qui deviennent des obstacles : *Stratégie de contournement*.
    **Attention, son propre bras est un obstacle, mais reste un chemin possible. Rien
     ne l'empêche d'envisager un retour en arrière jusq'uau point de montage intial ; 
     et les tâches en cours sont aussi des obstacles (leur points d'assemblages)** 
    *En effet, on ne veut pas qu'un robot en bloque un autre car son bras 
    empiète un point d'assemblage.*
    * Si deux robots entrent en conflits tête à tête :
        * Celui qui a la tâche avec le plus gros ratio est prioritaire. L'autre tente
        de le contourner en recalculant un chemin avec comme obstacle la place future du robot
        avec qui il est en conflit. Si aucun chemin ne l'emmène vers sont but, ou bien
        si ce chemin est trop long
            * Soit il abandonne la tâche en cours et il choisit une tâche libre plus 
            avantageuse,
            * Soit il attend.
    * Si un robot a fini ses tâches
        
        
#### III. Scoring et rédaction du fichier output

* Chaque robot doit être capable de donner son historique de ses positions. Il doit aussi
indiquer les tâches qu'il a réalisé, et celle qu'il a abandonné.
**Subtilité à pas oublier : si un robot abandonne toutes ses tâches, on ne l'indique pas dans
le fichier output.**
* Une fois que l'on a cela, on peut écrire le fichier output.
* On peut accessoirement calculer pour nous le score obtenu
* Ce serait cool aussi de pouvoir visualiser soius forme d'un gif le mouvement des robots
pour débuguer rapidement le code mais cela prendra beaucoup de temps et de place pour les 
grosses grilles

### Idées pour la structure du programme :
* Créations d'objets :
    * Robot : Se définit par son point de départ.  
        * Bouge
        * Est au courant des positions des autres robots
        * Reagit en cas de conflit
    * Tache : Se définit par ses points d'assemblage et par son score
        * Peut être libre/en cours/terminée
    * Grille : Se définit par sa taille, points de montages
        * Doit faire évoluer ses obstacles en fonction des cases occupées
        par les bras des robots
        * Contient la fonction permettant de calculer un trajet passant par des points donnés
        Cette fonction sera utilisée par les robots par exemple pour trouver de nouveaux chemins
        en cours de route, ou même au début pour calculer la longueur d'une tâche.
        **Bug à ne pas faire en créant cette fonction : quand un robot calcule la distance
        entre sa position et le début d'une tâche, il ne doit pas passer par le chemin nécessaire
        à la tâche actuelle, sinon il pourrait entrer en conflit avec lui-même**
        
* Corps du programme : Implémentation de la stratégie en elle-même.

**Probleme : Il faut être en capacité de dire si un robot
doit abandonner sa tâche pour la laisser à un autre. (cf problème
rencontré en visio)**

### Répartition des tâches
Robot, Distance, Grille, Tache 
* Alexis : Robot 
* Steven : Grille
* Clement : Tache
* Malo : Distance
