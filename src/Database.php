<?php
declare(strict_types=1);
require_once __DIR__.'/Clock.php';

final class Database
{
    public PDO $pdo;
    private int $savepoint=0;
    public function __construct(?array $config = null)
    {
        $config ??= require __DIR__ . '/../config/local.php';
        if (getenv('BD70_DATABASE')) {
            $name = getenv('BD70_DATABASE');
            if (!preg_match('/^bd70_[a-z0-9_]+$/', $name)) throw new RuntimeException('Base de test non autorisée.');
            $config['dsn'] = preg_replace('/dbname=[^;]+/', 'dbname=' . $name, $config['dsn']);
        }
        if (getenv('BD70_PORT')) {
            $port = filter_var(getenv('BD70_PORT'), FILTER_VALIDATE_INT, ['options'=>['min_range'=>1,'max_range'=>65535]]);
            if ($port === false) throw new RuntimeException('Port MariaDB invalide.');
            $config['dsn'] = preg_replace('/;port=[^;]+/', '', $config['dsn']);
            $config['dsn'] .= ';port='.$port;
        }
        date_default_timezone_set('Europe/Paris');
        $this->pdo = new PDO($config['dsn'], $config['user'], $config['password'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        $this->pdo->exec("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED");
        $this->pdo->exec("SET SESSION sql_mode='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'");
        // Recalculé à chaque connexion : Paris change d'offset en été/hiver.
        $instant=Clock::instant();
        $this->run('SET SESSION time_zone=?',[$instant->format('P')]);
        if(getenv('BD70_NOW')){
            $name=(string)$this->scalar('SELECT DATABASE()');
            if(!preg_match('/^bd70_(test|perf)[a-z0-9_]*$/',$name))throw new RuntimeException('Horloge fixe autorisée uniquement sur une base de recette.');
            $this->pdo->exec('SET timestamp='.(int)$instant->getTimestamp());
        }
    }
    public function run(string $sql, array $params = []): PDOStatement
    { $q = $this->pdo->prepare($sql); $q->execute($params); return $q; }
    public function all(string $sql, array $params = []): array { return $this->run($sql,$params)->fetchAll(); }
    public function one(string $sql, array $params = []): array
    { $r=$this->run($sql,$params)->fetch(); if (!$r) throw new DomainException('Élément introuvable.'); return $r; }
    public function scalar(string $sql, array $params = []): mixed { return $this->run($sql,$params)->fetchColumn(); }
    public function insert(string $table, array $data): int
    {
        // Table et colonnes viennent exclusivement du contrat PHP, jamais de SQL fourni par l'utilisateur.
        $cols=array_keys($data);
        $this->run('INSERT INTO `'.$table.'` (`'.implode('`,`',$cols).'`) VALUES ('.implode(',',array_fill(0,count($cols),'?')).')',array_values($data));
        return (int)$this->pdo->lastInsertId();
    }
    public function transaction(int $actor, callable $work): mixed
    {
        if($this->pdo->inTransaction()){
            $point='operation_'.(++$this->savepoint);$this->pdo->exec('SAVEPOINT '.$point);
            try{$result=$work();$this->pdo->exec('RELEASE SAVEPOINT '.$point);return $result;}
            catch(Throwable $e){$this->pdo->exec('ROLLBACK TO SAVEPOINT '.$point);$this->pdo->exec('RELEASE SAVEPOINT '.$point);throw $e;}
        }
        $this->pdo->beginTransaction();
        try {
            $this->run('SET @actor_id=?',[$actor]);
            $s=$this->run('CALL lock_site()'); $s->closeCursor();
            $result=$work(); $this->pdo->commit(); return $result;
        } catch (Throwable $e) { if ($this->pdo->inTransaction()) $this->pdo->rollBack(); throw $e; }
    }
}
