<?php
declare(strict_types=1);

final class Database
{
    public PDO $pdo;
    public function __construct(?array $config = null)
    {
        $config ??= require __DIR__ . '/../config/local.php';
        if (getenv('BD70_DATABASE')) {
            $name = getenv('BD70_DATABASE');
            if (!preg_match('/^bd70_[a-z0-9_]+$/', $name)) throw new RuntimeException('Base de test non autorisée.');
            $config['dsn'] = preg_replace('/dbname=[^;]+/', 'dbname=' . $name, $config['dsn']);
        }
        date_default_timezone_set($config['timezone'] ?? 'Europe/Paris');
        $this->pdo = new PDO($config['dsn'], $config['user'], $config['password'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        $this->pdo->exec("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED");
        $this->pdo->exec("SET SESSION sql_mode='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'");
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
        $this->pdo->beginTransaction();
        try {
            $this->run('SET @actor_id=?',[$actor]);
            $s=$this->run('CALL lock_site()'); $s->closeCursor();
            $result=$work(); $this->pdo->commit(); return $result;
        } catch (Throwable $e) { if ($this->pdo->inTransaction()) $this->pdo->rollBack(); throw $e; }
    }
}
