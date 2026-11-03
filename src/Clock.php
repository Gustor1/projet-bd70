<?php
declare(strict_types=1);

/** Heure civile du site ; l'horloge fixe est réservée aux commandes de recette. */
final class Clock
{
    public static function instant(): DateTimeImmutable
    {
        $zone=new DateTimeZone('Europe/Paris');
        $fixed=getenv('BD70_NOW');
        if(!$fixed)return new DateTimeImmutable('now',$zone);
        $date=DateTimeImmutable::createFromFormat('!Y-m-d H:i:s',$fixed,$zone);
        if(!$date||$date->format('Y-m-d H:i:s')!==$fixed)throw new RuntimeException('BD70_NOW doit être une date Paris valide.');
        return $date;
    }
    public static function now(): string { return self::instant()->format('Y-m-d H:i:s'); }
    public static function today(): string { return self::instant()->format('Y-m-d'); }
}
